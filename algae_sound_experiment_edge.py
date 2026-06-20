import csv
import platform
import time
from datetime import datetime
from pathlib import Path

if platform.system() == "Windows":
    from ctypes import POINTER, cast

    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, ISimpleAudioVolume

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait


# ============================================================
# 实验设置
# ============================================================

BASE_URL = "https://www.szynalski.com/tone-generator/"

# 需要播放的频率
FREQUENCIES = [200, 10000, 18000]

# 正式实验：每个频率 1 小时
FORMAL_DURATION_SECONDS = 60 * 60

# 测试模式：每个频率 10 秒
TEST_DURATION_SECONDS = 10

# 第一次运行建议 True
# 确认可以正常播放之后，改成 False
TEST_MODE = True

# 每个频率之间暂停时间
BREAK_BETWEEN_FREQ_SECONDS = 10

# 日志文件
LOG_FILE = "algae_sound_experiment_log.csv"


# ============================================================
# Windows 音量控制
# ============================================================

def set_windows_master_volume_to_100():
    """
    设置 Windows 系统主音量为 100%，并取消静音。
    兼容新版和旧版 pycaw。
    """
    if platform.system() != "Windows":
        print("[Volume] Skipped Windows master volume control on non-Windows system.")
        return

    speakers = AudioUtilities.GetSpeakers()

    try:
        # 新版 pycaw
        volume = speakers.EndpointVolume

    except AttributeError:
        # 旧版 pycaw
        interface = speakers.Activate(
            IAudioEndpointVolume._iid_,
            CLSCTX_ALL,
            None
        )
        volume = cast(interface, POINTER(IAudioEndpointVolume))

    volume.SetMute(0, None)
    volume.SetMasterVolumeLevelScalar(1.0, None)

    current_volume = volume.GetMasterVolumeLevelScalar()

    print("=" * 60)
    print(f"[Volume] Windows master volume set to {round(current_volume * 100)}%")
    print("=" * 60)


def set_edge_app_volume_to_100():
    """
    设置 Microsoft Edge 单独应用音量为 100%，并取消静音。
    Edge 必须已经打开，或者已经开始产生音频之后，才一定能找到 msedge.exe 的 audio session。
    """
    if platform.system() != "Windows":
        print("[Volume] Skipped Microsoft Edge app volume control on non-Windows system.")
        return

    sessions = AudioUtilities.GetAllSessions()
    found_edge = False

    for session in sessions:
        try:
            if session.Process and session.Process.name().lower() == "msedge.exe":
                volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                volume.SetMute(0, None)
                volume.SetMasterVolume(1.0, None)
                found_edge = True

        except Exception:
            continue

    if found_edge:
        print("[Volume] Microsoft Edge app volume set to 100%")
    else:
        print("[Volume] Microsoft Edge audio session not found yet. This can be normal before audio starts.")


# ============================================================
# Edge 浏览器设置
# ============================================================

def create_driver():
    """
    创建 Microsoft Edge 浏览器。
    """
    edge_options = Options()

    # 允许网页自动播放
    edge_options.add_argument("--autoplay-policy=no-user-gesture-required")

    # 减少后台网页暂停
    edge_options.add_argument("--disable-background-timer-throttling")
    edge_options.add_argument("--disable-backgrounding-occluded-windows")
    edge_options.add_argument("--disable-renderer-backgrounding")

    driver = webdriver.Edge(options=edge_options)
    driver.set_window_size(1200, 900)

    return driver


def wait_page_loaded(driver, timeout=20):
    """
    等待网页加载完成。
    """
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    time.sleep(2)


# ============================================================
# 网页操作
# ============================================================

def build_frequency_url(frequency):
    """
    用 URL hash 指定频率。

    例如：
    https://www.szynalski.com/tone-generator/#200
    """
    return f"{BASE_URL}#{frequency}"


def close_possible_popup(driver):
    """
    有时候网页会出现 Got it / OK / Accept 之类按钮。
    尝试自动点掉。
    """
    possible_texts = [
        "Got it",
        "OK",
        "I understand",
        "Accept"
    ]

    for text in possible_texts:
        try:
            elements = driver.find_elements(
                By.XPATH,
                f"//*[self::button or self::a][contains(text(), '{text}')]"
            )

            for element in elements:
                if element.is_displayed() and element.is_enabled():
                    element.click()
                    print(f"[Web] Closed popup/button: {text}")
                    time.sleep(1)
                    return

        except Exception:
            pass


def find_play_button(driver):
    """
    找 Play / Stop 按钮。
    根据之前 debug，网页按钮 id 是 play-button。
    """
    try:
        button = driver.find_element(By.ID, "play-button")

        if button.is_displayed() and button.is_enabled():
            return button

    except Exception:
        pass

    # 备用方案：根据文字找按钮
    candidates = driver.find_elements(
        By.XPATH,
        "//button | //input[@type='button'] | //a"
    )

    for element in candidates:
        try:
            if not element.is_displayed() or not element.is_enabled():
                continue

            text = (element.text or element.get_attribute("value") or "").strip().lower()

            if "play" in text or "stop" in text:
                return element

        except Exception:
            continue

    raise RuntimeError("Could not find Play/Stop button.")


def get_play_button_text(driver):
    """
    获取 Play / Stop 按钮当前文字。
    """
    try:
        button = find_play_button(driver)
        text = (button.text or button.get_attribute("value") or "").strip()
        return text

    except Exception:
        return ""


def click_play_if_needed(driver):
    """
    如果当前是 Play，就点击开始。
    如果当前是 Stop，说明已经在播放。
    """
    button = find_play_button(driver)
    text = (button.text or button.get_attribute("value") or "").strip().lower()

    if "play" in text:
        button.click()
        print("[Web] Clicked Play")
        time.sleep(1)

    elif "stop" in text:
        print("[Web] Already playing")

    else:
        button.click()
        print("[Web] Clicked main audio button")
        time.sleep(1)


def click_stop_if_needed(driver):
    """
    如果当前是 Stop，就点击停止。
    如果当前是 Play，说明已经停止。
    """
    button = find_play_button(driver)
    text = (button.text or button.get_attribute("value") or "").strip().lower()

    if "stop" in text:
        button.click()
        print("[Web] Clicked Stop")
        time.sleep(1)

    elif "play" in text:
        print("[Web] Already stopped")

    else:
        button.click()
        print("[Web] Clicked main audio button to stop")
        time.sleep(1)


def open_frequency_page(driver, frequency):
    """
    打开指定频率的网页。
    """
    url = build_frequency_url(frequency)

    print(f"[Web] Opening frequency URL: {url}")

    driver.get(url)
    wait_page_loaded(driver)
    close_possible_popup(driver)

    # 网页打开后 Edge audio session 可能才出现，所以这里再设置一次
    set_edge_app_volume_to_100()


# ============================================================
# 日志
# ============================================================

def write_log(row):
    """
    写入 CSV 实验日志。
    """
    file_exists = Path(LOG_FILE).exists()

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "date",
                "frequency_hz",
                "duration_seconds",
                "start_time",
                "end_time",
                "system",
                "browser",
                "master_volume",
                "edge_volume",
                "website",
                "status"
            ]
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)


# ============================================================
# 单个频率实验
# ============================================================

def run_one_frequency(driver, frequency, duration_seconds):
    """
    播放一个频率，计时，停止，并记录日志。
    """
    start_time = datetime.now()
    status = "success"

    print("=" * 60)
    print(f"开始播放：{frequency} Hz")
    print(f"开始时间：{start_time}")
    print(f"持续时间：{duration_seconds} 秒")
    print("=" * 60)

    try:
        # 每个频率重新打开对应链接
        open_frequency_page(driver, frequency)

        # 再次确认音量
        set_windows_master_volume_to_100()
        set_edge_app_volume_to_100()

        # 点击播放
        click_play_if_needed(driver)

        # 播放后 Edge audio session 更可能出现，所以再设一次 Edge 音量
        set_edge_app_volume_to_100()

        print(f"[Timer] {frequency} Hz 正在播放...")
        time.sleep(duration_seconds)

        # 停止播放
        click_stop_if_needed(driver)

    except Exception as error:
        status = f"failed: {error}"
        print(f"[Error] {status}")

        try:
            click_stop_if_needed(driver)
        except Exception:
            pass

    end_time = datetime.now()

    write_log({
        "date": start_time.date().isoformat(),
        "frequency_hz": frequency,
        "duration_seconds": duration_seconds,
        "start_time": start_time.isoformat(timespec="seconds"),
        "end_time": end_time.isoformat(timespec="seconds"),
        "system": "Windows",
        "browser": "Microsoft Edge",
        "master_volume": "100%",
        "edge_volume": "100%",
        "website": build_frequency_url(frequency),
        "status": status
    })

    print(f"结束播放：{frequency} Hz")
    print(f"结束时间：{end_time}")
    print(f"状态：{status}")


# ============================================================
# 主程序
# ============================================================

def main():
    duration = TEST_DURATION_SECONDS if TEST_MODE else FORMAL_DURATION_SECONDS

    print("Algae sound experiment automation started.")
    print(f"Test mode: {TEST_MODE}")
    print(f"Each frequency duration: {duration} seconds")
    print(f"Frequencies: {FREQUENCIES}")

    # 先设置 Windows 主音量
    set_windows_master_volume_to_100()

    driver = create_driver()

    try:
        # 先打开一次主页，让 Edge 进程和 audio session 出现
        driver.get(BASE_URL)
        wait_page_loaded(driver)
        close_possible_popup(driver)

        # 设置 Edge 单独应用音量
        set_edge_app_volume_to_100()

        for frequency in FREQUENCIES:
            run_one_frequency(driver, frequency, duration)

            if frequency != FREQUENCIES[-1]:
                print(f"暂停 {BREAK_BETWEEN_FREQ_SECONDS} 秒...")
                time.sleep(BREAK_BETWEEN_FREQ_SECONDS)

        print("=" * 60)
        print("所有频率播放完成。")
        print(f"日志已保存到：{LOG_FILE}")
        print("=" * 60)

    finally:
        print("关闭 Edge 浏览器...")
        driver.quit()


if __name__ == "__main__":
    main()
