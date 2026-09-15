# RAVEN QNX Build Configuration

# Set standard QNX SDP compiler if available, otherwise fallback to standard gcc for host-side stub tests
CC = qcc
# Target Raspberry Pi 4 (AArch64 / ARMv8)
TARGET_ARCH = -Vgcc_ntoaarch64le
CFLAGS = -Wall -O2

SRC_DIR = src
BIN_DIR = bin

TARGET = $(BIN_DIR)/sensor_bridge

all: setup $(TARGET)

setup:
	@mkdir -p $(BIN_DIR)

$(TARGET): $(SRC_DIR)/sensor_bridge.c
	$(CC) $(TARGET_ARCH) $(CFLAGS) -o $@ $<

clean:
	rm -rf $(BIN_DIR)
