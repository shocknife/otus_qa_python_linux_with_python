import subprocess
from collections import defaultdict
from datetime import datetime
import os


def get_ps_aux_output():
    try:
        result = subprocess.run(
            ["ps", "aux"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"Ошибка при выполнении команды ps aux: {result.stderr}")
        return result.stdout
    except Exception as e:
        print(f"Не удалось получить вывод команды ps aux: {e}")
        return ""


def parse_ps_output(output):
    if not output:
        return None

    users = set()
    process_count = 0
    user_processes = defaultdict(int)
    memory_usage = 0.0
    cpu_usage = 0.0
    max_memory_process = ("", 0.0)
    max_cpu_process = ("", 0.0)

    for line in output.splitlines()[1:]:
        parts = line.split()
        if len(parts) < 11:
            continue

        user = parts[0]
        cpu = float(parts[2])
        mem = float(parts[3])
        command = parts[10] if len(parts) > 10 else ""

        users.add(user)
        process_count += 1
        user_processes[user] += 1
        memory_usage += mem
        cpu_usage += cpu

        if mem > max_memory_process[1]:
            max_memory_process = (command, mem)

        if cpu > max_cpu_process[1]:
            max_cpu_process = (command, cpu)

    return {
        "users": users,
        "process_count": process_count,
        "user_processes": user_processes,
        "memory_usage": memory_usage,
        "cpu_usage": cpu_usage,
        "max_memory_process": max_memory_process,
        "max_cpu_process": max_cpu_process,
    }


def save_report(report):
    folder = "parser_scan"
    if not os.path.exists(folder):
        os.makedirs(folder)

    filename = os.path.join(folder, datetime.now().strftime("%d-%m-%Y-%H:%M-scan.txt"))

    try:
        with open(filename, "w") as f:
            f.write("Отчёт о состоянии системы:\n")
            f.write(f"Пользователи системы: {', '.join(report['users'])}\n")
            f.write(f"Процессов запущено: {report['process_count']}\n")
            f.write("\nПользовательских процессов:\n")

            for user, count in report["user_processes"].items():
                f.write(f"{user}: {count}\n")

            f.write(f"\nВсего памяти используется: {report['memory_usage']:.1f}%\n")
            f.write(f"Всего CPU используется: {report['cpu_usage']:.1f}%\n")

            f.write(
                f"\nБольше всего памяти использует: {report['max_memory_process'][0][:20]} ({report['max_memory_process'][1]:.1f}%)\n"
            )
            f.write(
                f"Больше всего CPU использует: {report['max_cpu_process'][0][:20]} ({report['max_cpu_process'][1]:.1f}%)\n"
            )
        print(f"Отчёт сохранён в файл {filename}")
    except Exception as e:
        print(f"Ошибка при сохранении отчёта в файл: {e}")


def main():
    output = get_ps_aux_output()
    if not output:
        print("Не удалось собрать информацию о процессах.")
        return

    report = parse_ps_output(output)
    if not report:
        print("Не удалось обработать вывод команды ps aux.")
        return

    print("Отчёт о состоянии системы:")
    print(f"Пользователи системы: {', '.join(report['users'])}")
    print(f"Процессов запущено: {report['process_count']}")
    print("\nПользовательских процессов:")
    for user, count in report["user_processes"].items():
        print(f"{user}: {count}")

    print(f"\nВсего памяти используется: {report['memory_usage']:.1f}%")
    print(f"Всего CPU используется: {report['cpu_usage']:.1f}%")

    print(
        f"\nБольше всего памяти использует: {report['max_memory_process'][0][:20]} ({report['max_memory_process'][1]:.1f}%)"
    )
    print(
        f"Больше всего CPU использует: {report['max_cpu_process'][0][:20]} ({report['max_cpu_process'][1]:.1f}%)"
    )

    save_report(report)


if __name__ == "__main__":
    main()
