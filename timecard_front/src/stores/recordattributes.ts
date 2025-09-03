import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '@/api/axios';
import type { RecordAttribute } from '@/types';


export const useRecordAttributesStore = defineStore('recordattributes', () => {
    const recordAttributes = ref<RecordAttribute[]>([]);

    const getRecordAttributes = async () => {
        try {
            const response = await api.get('/recordattributes');
            recordAttributes.value = response.data;
        } catch (error: any) {
            console.error('Request failed:', error.response?.data);
            throw error;
        }
    }

    async function updateRecordAttribute(attributeToUpdate: RecordAttribute) {
        try {
          const index = recordAttributes.value.findIndex(ra => ra.id === attributeToUpdate.id);
          if (index !== -1) {
            recordAttributes.value[index] = attributeToUpdate;
          }

          await api.put(`/recordattributes/${attributeToUpdate.id}`, attributeToUpdate);
          
        } catch (error) {
          console.error('Failed to update record attribute:', error);
        }
    }

    return {
        recordAttributes,
        getRecordAttributes,
        updateRecordAttribute,
    };
})
