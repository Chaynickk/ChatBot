export function useTelegram() {
  const tg = (window as any).Telegram?.WebApp

  const close = () => tg?.close()
  const expand = () => tg?.expand()

  return {
    tg,
    user: tg?.initDataUnsafe?.user,
    close,
    expand
  }
} 