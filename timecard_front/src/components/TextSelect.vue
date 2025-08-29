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

const isInputActive = ref<boolean>(false);
const displayText = computed(() => {
  if (typeof props.modelValue === 'object' && props.modelValue !== null) {
    return props.modelValue.name;
  }
  return props.modelValue;
})
const backgroundColor = computed(() => {
  if (typeof props.modelValue === 'object' && props.modelValue !== null) {
    return props.modelValue.color || '#777';
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
  'update:modelValue': [value: string];
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
  <div class="w-full rounded-md border border-gray-700"
       :style="{ backgroundColor: backgroundColor }" >
    <input type="text"
           class="p-2 w-full"
           :class="{ 'opacity-50 cursor-not-allowed text-gray-500': props.disabled}"
           :placeholder="props.placeholder"
           :value="displayText"
           :disabled="props.disabled"
           @input="updateValue"
           @focus="handleFocus"
           @blur="handleBlur">
    </input>
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
