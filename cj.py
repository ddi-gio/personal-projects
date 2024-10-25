import time
from datetime import datetime
import sys
import pyvisa as visa
from ddi_ecat_master import pysoem, Master
ECAT_IF = "eno4"
PDO_OFFSET = 22
RECORD_INTERVAL_SECONDS = 3
RPI_ROOT_DIR = "/home/ddi/code/safe_ain_hw_test/pi"
RPI_USER_NAME = "ddi"
RPI_IP_ADDR = "10.0.1.177"
DMM_IP_ADDR = "192.168.9.32"
def sleep_ns(ns):
    start = time.perf_counter_ns()
    while time.perf_counter_ns() < start + ns:
        pass
def read_dmm_voltage(dmm):
    return float(dmm.query("READ?"))
def open_dmm(ip):
    rm = visa.ResourceManager()
    rm.list_resources()
    dmm = rm.open_resource("TCPIP::" + ip + "::INSTR")
    dmm.read_termination = "\n"
    dmm.write_termination = "\n"
    return dmm
def list_to_csv(l: list):
    return ','.join([f'{word}' for word in l])
def read_ecat_data(master):
    master.receive_data()
    sleep_ns(400000)
    master.receive_data()
    raw_data = master.master.slaves[0].input[PDO_OFFSET:PDO_OFFSET+16]
    ch_data = []
    for i in range(0, len(raw_data), 2):
        ch_data.append(int(raw_data[i] + (raw_data[i+1] << 8)) / 16) # ECAT data units are 16ths of a degC, so divide by 16 here to convert to degC
    return ch_data
if __name__ == "__main__":
    # Instrument and card setup
    dmm = open_dmm(DMM_IP_ADDR)
    now = datetime.now()
    f = open(f"cj_qual-{now.strftime('%Y%m%d-%H%M')}.csv", "w")
    f.write("Time,DMM_VOLTS,ECAT0,ECAT1,ECAT2,ECAT3,ECAT4,ECAT5,ECAT6,ECAT7\n")
    try:
        master = Master()
        master.connect()
        master.init()
    except Exception as e:
        master.close(ECAT_IF)
        raise
    master.state_request(pysoem.OP_STATE)
    while True:
        try:
            sleep_ns(RECORD_INTERVAL_SECONDS*1e9 - 400000)
            ecat_data = read_ecat_data(master)
            dmm_data = read_dmm_voltage(dmm)
            print(f"{datetime.now().strftime('%H:%M:%S.%f')},{dmm_data},{list_to_csv(ecat_data)}")
            f.write(f"{datetime.now().strftime('%H:%M:%S.%f')},{dmm_data},{list_to_csv(ecat_data)}\n")
        except KeyboardInterrupt:
            f.close()
            sys.exit()
 
has context menu


has context menu
