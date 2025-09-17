import asyncio
from kasa import SmartBulb

async def main():
    bulb = SmartBulb("172.20.10.13")  # usa o IP que encontraste

    await bulb.update()
    print(f"💡 Lâmpada encontrada: {bulb.alias}")
    print("Estado atual:", "Ligada" if bulb.is_on else "Desligada")

    # Comandos
    print("🔁 A alternar o estado da lâmpada...")
    if bulb.is_on:
        await bulb.turn_off()
        print("🔌 Lâmpada desligada.")
    else:
        await bulb.turn_on()
        print("⚡ Lâmpada ligada.")

    # Brilho (opcional)
    await bulb.set_brightness(60)  # valores de 0 a 100
    print("✨ Brilho ajustado para 60%.")

if __name__ == "__main__":
    asyncio.run(main())
