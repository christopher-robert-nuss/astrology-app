import { ref } from 'vue'

const message = ref(null)
let clearTimer = null
let nextId = 0

const clearTimerIfAny = () => {
  if (clearTimer == null) return
  clearTimeout(clearTimer)
  clearTimer = null
}

export function useStatusMessage() {
  const show = ({ tone = 'ok', text, life } = {}) => {
    const copy = String(text || '').trim()
    if (!copy) return

    clearTimerIfAny()
    nextId += 1
    const id = nextId
    const sticky = tone === 'problem' && (life == null || life === 0)
    const duration = life ?? (tone === 'problem' ? 0 : 2500)

    message.value = { id, tone, text: copy, sticky }

    if (duration > 0) {
      clearTimer = setTimeout(() => {
        if (message.value?.id === id) message.value = null
        clearTimer = null
      }, duration)
    }
  }

  const clear = () => {
    clearTimerIfAny()
    message.value = null
  }

  return { message, show, clear }
}

if (import.meta.env.DEV && typeof window !== 'undefined') {
  window.__astroStatus = useStatusMessage()
}
