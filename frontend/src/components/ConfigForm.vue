<template>
  <div class="space-y-5">
    <!-- Provider preset -->
    <div>
      <label class="label">服务商预设（快速填充 Base URL）</label>
      <div class="grid grid-cols-3 gap-2">
        <button
          v-for="p in PROVIDERS"
          :key="p.name"
          type="button"
          class="py-1.5 px-2 rounded-lg text-xs font-medium border border-gray-700 text-gray-300 hover:border-brand-500 hover:text-brand-500 transition"
          @click="applyProvider(p)"
        >
          {{ p.name }}
        </button>
      </div>
    </div>

    <!-- Model -->
    <div>
      <label class="label">模型 (model)</label>
      <div class="flex gap-2">
        <select v-model="cfg.model" class="input flex-1">
          <option v-for="m in MODELS" :key="m" :value="m">{{ m }}</option>
          <option value="__custom__">自定义...</option>
        </select>
        <input
          v-if="cfg.model === '__custom__'"
          v-model="customModel"
          class="input flex-1"
          placeholder="provider/model-name 或 gpt-4o"
        />
      </div>
    </div>

    <!-- API Base URL -->
    <div>
      <label class="label">API 地址 (base_url)</label>
      <input
        v-model="cfg.base_url"
        type="text"
        class="input font-mono text-xs"
        placeholder="https://openrouter.ai/api/v1  (留空使用模型对应官方默认)"
        autocomplete="off"
      />
      <p class="mt-1 text-xs text-gray-500">
        OpenRouter、Ollama、One-API、自建网关等第三方需填写。Anthropic / OpenAI 官方直连可留空
      </p>
    </div>

    <!-- API Key -->
    <div>
      <label class="label">API Key</label>
      <input
        v-model="cfg.api_key"
        type="password"
        class="input"
        placeholder="sk-..."
        autocomplete="off"
      />
      <p class="mt-1 text-xs text-gray-500">与上方 API 地址匹配的密钥</p>
    </div>

    <!-- Reasoning effort -->
    <div>
      <label class="label">推理强度 (reasoning_effort)</label>
      <div class="flex gap-2">
        <button
          v-for="opt in EFFORTS"
          :key="opt"
          type="button"
          class="flex-1 py-1.5 rounded-lg text-xs font-medium border transition"
          :class="
            cfg.reasoning_effort === opt
              ? 'bg-brand-500 border-brand-500 text-white'
              : 'bg-transparent border-gray-700 text-gray-400 hover:border-gray-500'
          "
          @click="cfg.reasoning_effort = opt"
        >
          {{ opt }}
        </button>
      </div>
    </div>

    <!-- Language -->
    <div>
      <label class="label">界面语言 (language)</label>
      <div class="flex gap-2 flex-wrap">
        <button
          v-for="opt in LANGUAGES"
          :key="opt.value"
          type="button"
          class="py-1.5 px-3 rounded-lg text-xs font-medium border transition"
          :class="
            cfg.language === opt.value
              ? 'bg-brand-500 border-brand-500 text-white'
              : 'bg-transparent border-gray-700 text-gray-400 hover:border-gray-500'
          "
          @click="cfg.language = opt.value"
        >
          {{ opt.label }}
        </button>
      </div>
      <p class="mt-1 text-xs text-gray-500">影响审批提示、网关斜杠命令回复等静态文案；不影响 AI 回复语言</p>
    </div>

    <!-- Max turns -->
    <div>
      <label class="label">最大轮次 (max_turns) — {{ cfg.max_turns }}</label>
      <input
        v-model.number="cfg.max_turns"
        type="range"
        min="10"
        max="200"
        step="10"
        class="w-full accent-brand-500"
      />
      <div class="flex justify-between text-xs text-gray-600 mt-0.5">
        <span>10</span><span>200</span>
      </div>
    </div>

    <!-- Extra YAML -->
    <div>
      <label class="label">附加配置 (YAML 格式，追加到 cli-config.yaml)</label>
      <textarea
        v-model="cfg.extra_yaml"
        class="input font-mono text-xs resize-y"
        rows="6"
        placeholder="tools:&#10;  exa_api_key: sk-exa-xxx&#10;  fal_api_key: xxx"
      />
    </div>

    <!-- Slot for submit button -->
    <slot :config="currentConfig" />
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: Object, default: () => ({}) },
})
const emit = defineEmits(['update:modelValue'])

const MODELS = [
  'anthropic/claude-opus-4-5',
  'anthropic/claude-sonnet-4-5',
  'anthropic/claude-haiku-4-5',
  'openai/gpt-4o',
  'openai/gpt-4o-mini',
  'google/gemini-2.0-flash-001',
  'meta-llama/llama-3.3-70b-instruct',
  'deepseek/deepseek-chat',
  'qwen/qwen-2.5-72b-instruct',
]

const EFFORTS = ['xhigh', 'high', 'medium', 'low', 'minimal']

const LANGUAGES = [
  { value: 'zh', label: '中文' },
  { value: 'en', label: 'English' },
  { value: 'ja', label: '日本語' },
  { value: 'de', label: 'Deutsch' },
  { value: 'es', label: 'Español' },
  { value: 'fr', label: 'Français' },
  { value: 'tr', label: 'Türkçe' },
  { value: 'uk', label: 'Українська' },
]

const PROVIDERS = [
  { name: 'Anthropic 官方', base_url: '' },
  { name: 'OpenAI 官方', base_url: '' },
  { name: 'OpenRouter', base_url: 'https://openrouter.ai/api/v1' },
  { name: '智谱 GLM', base_url: 'https://open.bigmodel.cn/api/paas/v4' },
  { name: 'DeepSeek', base_url: 'https://api.deepseek.com/v1' },
  { name: 'Moonshot', base_url: 'https://api.moonshot.cn/v1' },
  { name: 'Ollama 本地', base_url: 'http://localhost:11434/v1' },
  { name: 'One-API', base_url: 'http://localhost:3000/v1' },
  { name: 'Gemini', base_url: 'https://generativelanguage.googleapis.com/v1beta/openai' },
]

const cfg = reactive({
  model: 'anthropic/claude-opus-4-5',
  api_key: '',
  base_url: '',
  reasoning_effort: 'high',
  max_turns: 60,
  language: 'zh',
  extra_yaml: '',
})

const customModel = ref('')

function applyProvider(p) {
  cfg.base_url = p.base_url
}

// Sync incoming value → local state
watch(
  () => props.modelValue,
  (v) => {
    if (!v) return
    const known = MODELS.includes(v.model)
    cfg.model = known ? v.model : '__custom__'
    customModel.value = known ? '' : (v.model || '')
    cfg.api_key = v.api_key || ''
    cfg.base_url = v.base_url || ''
    cfg.reasoning_effort = v.reasoning_effort || 'high'
    cfg.max_turns = v.max_turns ?? 60
    cfg.language = v.language || 'zh'
    cfg.extra_yaml = v.extra_yaml || ''
  },
  { immediate: true, deep: true },
)

const currentConfig = computed(() => ({
  model: cfg.model === '__custom__' ? customModel.value : cfg.model,
  api_key: cfg.api_key,
  base_url: cfg.base_url,
  reasoning_effort: cfg.reasoning_effort,
  max_turns: cfg.max_turns,
  language: cfg.language,
  extra_yaml: cfg.extra_yaml,
}))

// Emit upstream whenever anything changes
watch(currentConfig, (v) => emit('update:modelValue', v), { deep: true })
</script>

