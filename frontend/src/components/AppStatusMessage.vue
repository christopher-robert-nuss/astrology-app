<template>
  <Teleport to="body">
    <div
      v-if="message"
      class="astro-status"
      :class="statusClass"
      :style="statusStyle"
      :data-tone="message.tone"
      role="status"
      :aria-live="message.tone === 'problem' ? 'assertive' : 'polite'"
    >
      <p class="astro-status-text">{{ message.text }}</p>
      <button
        v-if="message.sticky"
        type="button"
        class="astro-status-dismiss"
        aria-label="Dismiss"
        @click="clear"
      >
        ×
      </button>
    </div>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import { useStatusMessage } from '../composables/useStatusMessage.js'

const { message, clear } = useStatusMessage()

const isStrip = computed(() => {
  if (!message.value) return false
  if (message.value.tone === 'problem') return true
  return message.value.text.length > 36
})

const statusClass = computed(() => [
  isStrip.value ? 'astro-status--strip' : 'astro-status--inline',
  message.value?.tone === 'problem' ? 'astro-status--problem' : 'astro-status--ok',
])

const statusStyle = computed(() =>
  isStrip.value
    ? {
        position: 'fixed',
        top: 'var(--astro-menu-height)',
        right: '0',
        left: '0',
        zIndex: 2000,
      }
    : {
        position: 'fixed',
        top: '0',
        right: '14px',
        zIndex: 2000,
      },
)
</script>
