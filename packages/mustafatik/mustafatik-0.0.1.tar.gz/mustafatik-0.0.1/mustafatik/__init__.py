import random
import time

class mustafatik:
    def __init__(self):
        self.devices = [
            "Samsung Galaxy A10","Samsung Galaxy A11","Samsung Galaxy A12","Samsung Galaxy A20",
            "Samsung Galaxy A21","Samsung Galaxy A22","Samsung Galaxy A30","Samsung Galaxy A31",
            "Samsung Galaxy A32","Samsung Galaxy A33","Samsung Galaxy A50","Samsung Galaxy A51",
            "Samsung Galaxy A52","Samsung Galaxy A53","Samsung Galaxy A54","Samsung Galaxy S20",
            "Samsung Galaxy S21","Samsung Galaxy S22","Samsung Galaxy S23","Samsung Galaxy M11",
            "Samsung Galaxy M12","Samsung Galaxy M21","Samsung Galaxy M31","Samsung Galaxy M51",
            "Xiaomi Redmi 9","Xiaomi Redmi 9A","Xiaomi Redmi 10","Xiaomi Redmi 10A",
            "Xiaomi Redmi Note 8","Xiaomi Redmi Note 9","Xiaomi Redmi Note 10",
            "Xiaomi Redmi Note 11","Xiaomi Redmi Note 12","Xiaomi Poco X3","Xiaomi Poco X3 Pro",
            "Xiaomi Poco F3","Xiaomi Poco F4","OPPO A15","OPPO A16","OPPO A31","OPPO A53",
            "OPPO Reno 5","OPPO Reno 6","Vivo Y12","Vivo Y15","Vivo Y20","Vivo Y21","Vivo Y33",
            "Vivo V20","Vivo V21","Huawei Y7 Prime","Huawei Y9 2019","Huawei Nova 3i",
            "Huawei Nova 7i","Huawei Mate 20 Lite","Huawei P30 Lite","Infinix Hot 9",
            "Infinix Hot 10","Infinix Hot 11","Infinix Hot 12","Infinix Note 7","Infinix Note 8",
            "Infinix Note 10","Infinix Note 11","Tecno Spark 6","Tecno Spark 7",
            "Tecno Spark 8","Tecno Camon 15","Tecno Camon 16","Motorola Moto G7",
            "Motorola Moto G8","Motorola Moto G9","Motorola Moto G10","Motorola Moto G30",
            "Motorola Moto E7","Nokia 3.4","Nokia 5.3","Nokia 5.4","Nokia X10","Nokia X20"
        ] * 5

    def _device(self):
        device = random.choice(self.devices)
        android = random.choice(["10","11","12","13","14"])
        build = f"SP1A.{random.randint(200000,299999)}.{random.randint(100,999)}"
        ua = (
            f"Mozilla/5.0 (Linux; Android {android}; {device}) "
            f"AppleWebKit/537.36 (KHTML, like Gecko) "
            f"Chrome/112.0.0.0 Mobile Safari/537.36 "
            f"Build/{build}"
        )
        ts = str(round(random.uniform(1.2, 1.6) * 100000000) * -1)
        return {
            "device_type": device,
            "device_brand": device.split()[0],
            "android_version": android,
            "build_number": build,
            "user_agent": ua,
            "ts": ts,
            "_rticket": ts + "4632",
            "device_id": str(random.randint(1, 10**19))
        }

    def updateParams(self, params: dict):
        self._last_device = self._device()
        d = self._last_device
        params.update({
            "device_type": d["device_type"],
            "device_brand": d["device_brand"],
            "android_version": d["android_version"],
            "build_number": d["build_number"],
            "device_id": d["device_id"],
            "ts": d["ts"],
            "_rticket": d["_rticket"],
            "user_agent": d["user_agent"]
        })
        return params

    def updateHeaders(self, headers: dict):
        d = getattr(self, "_last_device", None)
        if d is None:
            d = self._device()
            self._last_device = d
        headers.update({
            "User-Agent": d["user_agent"]
        })
        return headers