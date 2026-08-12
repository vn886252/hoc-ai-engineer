class TaiKhoanNganHang:
    def __init__(self, chu_so_huu, so_du):
        self.chu_so_huu = chu_so_huu
        self.so_du = so_du
    
    def nap_tien(self, so_tien):
        self.so_du = self.so_du + so_tien
        return self.so_du + so_tien

    def rut_tien(self, so_tien):
        if self.so_du >= so_tien:
          self.so_du = self.so_du - so_tien
          return self.so_du
        else:
            print("So du khong du")
            return self.so_du

tk1 = TaiKhoanNganHang("Minh",5000)
print(tk1.nap_tien(5000))
print(tk1.rut_tien(6000))
print(tk1.rut_tien(100000))