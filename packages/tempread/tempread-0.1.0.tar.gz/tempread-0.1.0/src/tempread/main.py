import psutil
import sys

def get_cpu_temp():
    temps = psutil.sensors_temperatures()

    if not temps:
        print("No CPU temperature sensors found")
        return

    print(f"{'Sensor':<20} | {'Current':<10} | {'Critical':<10}")
    print("-" * 46)

    found = False
    for name, entries in temps.items():
        for entry in entries:
            if entry.current:
                current = f"{entry.current}°C"
                critical = f"{entry.critical}°C" if entry.critical and entry.critical < 200 else "N/A"

                print(f"{entry.label or name:<20} | {current:<10} | {critical:<10}")
                found = True

    if not found:
        print("Sensors found, but no temperature data available.")

def main():
    try:
        get_cpu_temp()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"A error occurred: {e}")


if __name__ == "__main__":
    main()