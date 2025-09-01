<script setup lang="ts">
import type { RecordAttribute, TimeRecord } from '@/types';
import { secondaryColor } from '@/utils/colorUtils';
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
    return secondaryColor(props.modelValue.color);
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
       :style="{ backgroundColor: backgroundColor, borderColor: modelValue.color ? modelValue.color : '#333' }" >
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
