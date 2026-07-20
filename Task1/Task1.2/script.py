# got the logic from here - simple 1st complement that already exists online 0.0 but i understand how it works 

class TicketCoded():
    def __init__(self, ticket_code: str):
        self.ticket_code = ticket_code
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


    def encode(self , ticket_id : str):
        pass
    
    def decode(self , barcode):
        pass
    
    
