# got the logic from here - simple 1st complement that already exists online 0.0 but i understand how it works 

class TicketCoded():
    def __init__(self):
        self.MASK16 = 0xFFFF
        self.SEP    = "#"
        self.CHECKSUM_HEX_LEN = 4 #16 bits
    
    #
    def _ones_complement_sum(self, data: bytes) -> int:
        # pad to even length with a zero byte so we can group into 16-bit words
        if len(data) % 2 == 1:
            data += b'\x00'

        total = 0
        for i in range(0, len(data), 2):
            word = (data[i] << 8) + data[i + 1]   # combine 2 bytes -> 16-bit word
            total += word
            # end-around carry: fold any overflow past bit 16 back in
            total = (total & self.MASK16) + (total >> 16)

        return total & self.MASK16

    def _compute_checksum(self, ticket_id: str) -> int:
        data = ticket_id.encode("utf-8")
        summed = self._ones_complement_sum(data)
        checksum = (~summed) & self.MASK16   # one's complement (bitwise NOT)
        return checksum


    def encode(self, ticket_id: str) -> str:
        checksum = self._compute_checksum(ticket_id)
        checksum_hex = format(checksum, f"0{self.CHECKSUM_HEX_LEN}X")
        return f"{ticket_id}{self.SEP}{checksum_hex}"
    
    def decode(self, barcode: str):
            if self.SEP not in barcode:
                return "CORRUPTED"

            ticket_id, checksum_hex = barcode.rsplit(self.SEP, 1)

            try:
                embedded_checksum = int(checksum_hex, 16)
            except ValueError:
                return "CORRUPTED"

            # verification via the classic "sum + checksum -> all 1s -> 0" trick ---
            data = ticket_id.encode("utf-8")
            data_sum = self._ones_complement_sum(data)
            total = data_sum + embedded_checksum
            total = (total & self.MASK16) + (total >> 16)  # end-around carry once more

            if total == self.MASK16:  #0xFFFF means its working correctly
                return ticket_id
            else:
                recomputed = self._compute_checksum(ticket_id)
                return (f"CORRUPTED: checksum mismatch "
                        f"(expected {format(recomputed, '04X')}, got {checksum_hex})")
        
if __name__ == "__main__":
    codec = TicketCoded()

    sample_ids = ["TKT12345", "VIP0042A", "GA2026XZ9"]

    barcodes = []
    print("Encoding")
    for id in sample_ids:
        bc = codec.encode(id)
        barcodes.append(bc)
        print(f"{id:12s} -> {bc}")

    print("\nDecoding (unmodified)")
    for bc in barcodes:
        result = codec.decode(bc)
        print(f"{bc:16s} -> {result}")

    print("tampered")
    for bc in barcodes:
        ticket_part, checksum_part = bc.split(codec.SEP)
        idx = 1  # corrupt one character in the ticket portion
        new_char = "Q" if ticket_part[idx] != "Q" else "Z"
        corrupted_ticket = ticket_part[:idx] + new_char + ticket_part[idx+1:]
        corrupted = f"{corrupted_ticket}{codec.SEP}{checksum_part}"
        result = codec.decode(corrupted)
        print(f"{bc} -> corrupted -> {corrupted:16s} -> {result}")
