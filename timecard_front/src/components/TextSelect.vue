<script setup lang="ts">
import type { RecordAttribute, TimeRecord } from '@/types';
import { ref, computed } from 'vue';

const props = defineProps<{
  placeholder: string;
  modelValue: RecordAttribute | string;
  recordAttributes: RecordAttribute[];
  parentRecordAttribute: RecordAttribute | string | null;
  levelNum: number;
  disabled?: boolean;
}>();

const darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
const isDarkMode = ref(darkModeMediaQuery.matches);

const isInputActive = ref<boolean>(false);
const displayText = computed(() => {
  if (typeof props.modelValue === 'object' && props.modelValue !== null) {
    return props.modelValue.name;
  }
  return props.modelValue;
});

const backgroundColor = computed(() => {
  if (typeof props.modelValue === 'object' && props.modelValue !== null && props.modelValue.color !== null) {
    // converting to hsl
    const r = parseInt(props.modelValue.color.slice(1, 3), 16) / 255;
    const g = parseInt(props.modelValue.color.slice(3, 5), 16) / 255;
    const b = parseInt(props.modelValue.color.slice(5), 16) / 255;

    const minVal = Math.min(r, g, b);
    const maxVal = Math.max(r, g, b);

    let h = 0;
    if (maxVal === r) {
      h = (g - b) / (maxVal - minVal);        
    } else if (maxVal === g) {
      h = 2.0 + (b - r)/(maxVal - minVal);
    } else {
      h = 4.0 + (r - g)/ (maxVal - minVal);
    }
    h *= 60;

    let l = (maxVal + minVal) / 2;

    let s = 0;
    if (maxVal - minVal !== 0) {
      s = (maxVal - minVal) / (1 - Math.abs(2 * l - 1));
    }

    // check the lightness against the theme
    if (isDarkMode.value) {
      l = Math.min(l, 0.25);
    } else {
      l = Math.max(l, 0.75);
    }

    // back to rgb
    let c = (1 - Math.abs(2 * l - 1)) * s;
    let x = c * (1 - Math.abs((h / 60) % 2 - 1));
    let m = l - c/2;
    let rp = 0;
    let gp = 0;
    let bp = 0;
    if (h < 60)       { rp = c, gp = x, bp = 0 }
    else if (h < 120) { rp = x, gp = c, bp = 0 }
    else if (h < 180) { rp = 0, gp = c, bp = x }
    else if (h < 240) { rp = 0, gp = x, bp = c }
    else if (h < 300) { rp = x, gp = 0, bp = c }
    else              { rp = c, gp = 0, bp = x }

    const rpp = Math.round((rp+m)*255);
    const gpp = Math.round((gp+m)*255);
    const bpp = Math.round((bp+m)*255);
    return `#${rpp.toString(16).padStart(2, '0')}${gpp.toString(16).padStart(2, '0')}${bpp.toString(16).padStart(2, '0')}`;
  }
  else if (typeof props.modelValue === 'object' && props.modelValue !== null) {
    return isDarkMode.value ? '#333' : '#ddd';
  }
  return 'transparent';
});

const suggestions = computed(() => {
  return props.recordAttributes.filter(ra => {
    let valid = true;
    valid = valid && (ra.level_num === props.levelNum);
    if (typeof props.parentRecordAttribute === 'object' && props.parentRecordAttribute !== null) {
      valid = valid && (ra.parent_id == props.parentRecordAttribute.id);
    } else if (props.levelNum > 1) {
      valid = false;
    }
    return valid;
  })
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: RecordAttribute | string): void
}>();

const updateValue = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const matchingAttribute = suggestions.value.find(ra => ra.name === target.value);
  if (matchingAttribute) {
    emit('update:modelValue', matchingAttribute);
    return;
  }
  emit('update:modelValue', target.value);
};

const handleFocus = () => {
  isInputActive.value = true;
}

const handleBlur = () => {
  isInputActive.value = false;
}

const selectRecordAttribute = (ra: RecordAttribute) => {
  emit('update:modelValue', ra);
}

</script>

<template>
  <div class="w-full rounded-md border border-gray-300 dark:border-gray-700"
       :class="{ 'ring-2': isInputActive }"
       :style="{ backgroundColor: backgroundColor}" >
    <div class="flex items-baseline">
      <input type="text"
             class="p-2 w-full bg-transparent focus:outline-none flex-grow"
             :class="{ 'opacity-50 cursor-not-allowed text-gray-500': props.disabled}"
             :placeholder="props.placeholder"
             :value="displayText"
             :disabled="props.disabled"
             @input="updateValue"
             @focus="handleFocus"
             @blur="handleBlur">
      </input>
    </div>
    <Transition name="wipe">
      <div v-if="isInputActive" class="overflow-hidden">
        <template v-for="ra in suggestions">
          <span class="px-2 cursor-pointer border rounded-sm m-2 inline-block" @click="selectRecordAttribute(ra)">{{ ra.name }}</span>
        </template>
      </div>
    </Transition>
  </div>
</template>

<style scoped>

.wipe-enter-active,
.wipe-leave-active {
  transition: max-height 0.2s ease;
}

.wipe-enter-from,
.wipe-leave-to {
  max-height: 0;
}

.wipe-enter-to,
.wipe-leave-from {
  max-height: 50rem; /* Adjust this value to fit your content */
}
</style>
