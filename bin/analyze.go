package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"sync"
	"time"

	_ "github.com/go-sql-driver/mysql"
	"github.com/google/gopacket"
	"github.com/google/gopacket/layers"
	"github.com/google/gopacket/pcap"
)

var (
	commit_interval time.Duration
	devices         []string          = []string{"tunUDP", "tunTCP"}
	snapshot_len    int32             = 65535
	promiscuous     bool              = false
	packets         map[string]uint32 = make(map[string]uint32)
	mutex           sync.Mutex
	db              *sql.DB
)

func commitPackets() {

	//Copy packets to local map to free the mutex asap
	mutex.Lock()
	localpackets := make(map[string]uint32)
	for ip, nb := range packets {
		localpackets[ip] = nb
	}
	packets = make(map[string]uint32)
	mutex.Unlock()

	tx, err := db.Begin()
	if err != nil {
		fmt.Println("Impossible to start transaction when commiting packets. Packets will not be updated in DB")
		return
	}
	defer tx.Commit()
	updStmt, err := tx.Prepare("UPDATE laborations_statistics " +
		"SET nb_packets = nb_packets + ? " +
		"WHERE lab_id = (SELECT laborations.ID FROM laborations " +
		"					INNER JOIN connected_clients c1 on c1.ID = laborations.init_academy " +
		"					INNER JOIN connected_clients c2 on c2.ID = laborations.invited_academy " +
		"					WHERE c1.virt_ip IS NOT NULL  " +
		"					AND c2.virt_ip IS NOT NULL " +
		"					AND (c1.virt_ip =? " +
		"					OR c2.virt_ip = ?) " +
		"					GROUP BY laborations.ID, laborations.started_at " +
		"					HAVING laborations.started_at = max(laborations.started_at) " +
		"               )")
	if err != nil {
		fmt.Println("Impossible to create prepared starement when commiting packets. Packets will not be updated in DB")
		return
	}
	defer updStmt.Close()
	for ip, nb := range localpackets {
		_, err := updStmt.Exec(nb, ip, ip)
		if err != nil {
			fmt.Println("Impossible to execute statement for IP " + ip + " when commiting packets. This IP's packets will not be updated in DB")
		}
	}

}

func capturePackets(iface string) {
	handle, err := pcap.OpenLive(iface, snapshot_len, promiscuous, pcap.BlockForever)
	if err != nil {
		log.Fatal(err)
	}
	defer handle.Close()
	err = handle.SetBPFFilter("dst host 172.16.100.1 and udp dst port 4789")
	if err != nil {
		log.Fatal(err)
	}
	packetSource := gopacket.NewPacketSource(handle, handle.LinkType())
	for packet := range packetSource.Packets() {
		ipLayer := packet.Layers()[0].(*layers.IPv4)
		srcip := ipLayer.SrcIP.String()
		mutex.Lock()
		packets[srcip] = packets[srcip] + 1
		mutex.Unlock()
	}
}

func doEvery(d time.Duration, f func()) {
	for range time.Tick(d) {
		f()
	}
}

func loadConfig(path string) map[string]interface{} {

	jsonFile, err := os.Open(path)
	if err != nil {
		fmt.Println(err)
	}
	defer jsonFile.Close()

	byteValue, _ := ioutil.ReadAll(jsonFile)

	var result map[string]interface{}
	json.Unmarshal([]byte(byteValue), &result)
	return result
}
func main() {
	var err error
	config := loadConfig("includes/config.json")
	commit_interval = time.Second * time.Duration(int(config["COMMIT_INTERVAL"].(float64)))
	//Open database
	connectionString := config["DB_TB_USER"].(string) + ":" + config["DB_TB_PASS"].(string) + "@tcp(" + config["DB_TB_HOST"].(string) + ")/" + config["DB_TB_NAME"].(string)
	db, err = sql.Open("mysql", connectionString)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	//Check connectivity with db
	err = db.Ping()
	if err != nil {
		log.Fatal(err)
	}
	for _, iface := range devices {
		go capturePackets(iface)
	}
	doEvery(commit_interval, commitPackets)
}

