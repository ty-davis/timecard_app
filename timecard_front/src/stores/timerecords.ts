import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '@/api/axios';
import type { TimeRecord, RecordAttribute } from '@/types';

const twoWeeksAgo = new Date(new Date().getTime() - (14 * 24 * 60 * 60 * 1000));
const oneWeekFromNow = new Date(new Date().getTime() + (7 * 24 * 60 * 60 * 1000));
let currentStart = new Date(twoWeeksAgo);
let currentEnd = new Date(oneWeekFromNow);

export const useTimeRecordsStore = defineStore('timerecords', () => {
    const timeRecords = ref<TimeRecord[]>([]);

    // calculate start date
    const startDate = twoWeeksAgo; 

    startDate.setHours(0);
    startDate.setMinutes(0);
    startDate.setSeconds(0);
    startDate.setMilliseconds(0);

    const start = ref<Date>(startDate);
    const end = ref<Date>(new Date());
    const filteredRecords = computed(() => {
        return timeRecords.value.filter((r: TimeRecord) => (start.value < new Date(r.timein) && new Date(r.timein) < end.value));
    })

    const getTimeRecords = async (force?: boolean, start?: Date, end?: Date) => {
        // decide whether it is worth doing the request based on the dates
        let makeRequest = false;

        if (force) {
            makeRequest = true;
        }
        if (!(timeRecords.value?.length > 0)) {
            makeRequest = true;
        }
        if (start) {
            if (start <= currentStart) { makeRequest = true }
        }
        if (end) {
            if (end >= currentEnd) { makeRequest = true }
        }

        if (!makeRequest) {
            console.log("Don't need to make a request now!");
            return;
        }

        const params: { start_date?: string, end_date?: string } = {};
        params.start_date = start ? start.toISOString() : currentStart.toISOString();
        params.end_date = end ? end.toISOString() : currentEnd.toISOString();
        
        try {
            const response = await api.get('/timerecords', { params });
            timeRecords.value = response.data;
        } catch (error: any) {
            console.error('Request failed:', error.response?.data);
            throw error;
        }
    }

    const saveTimeRecord = async (newRecord: TimeRecord) => {
        try {
            const response = await api.post('/timerecords', newRecord);
        } catch (error: any) {
            console.error('Failed to save record:', error.response?.data);
        }
    }

    const updateTimeRecord = async (updatedRecord: TimeRecord) => {
        try {
            const response = await api.put(`/timerecords/${updatedRecord.id}`, updatedRecord);
        } catch (error: any) {
            console.error('Failed to save record:', error.response?.data);
        }
    }

    const deleteTimeRecord = async (recordToDelete: TimeRecord) => {
        try {
            await api.delete(`/timerecords/${recordToDelete.id}`);
            timeRecords.value = timeRecords.value.filter((r: TimeRecord) => r.id !== recordToDelete.id);
        } catch (error: any) {
            console.error('Failed to delete record:', error.response?.data);
            throw error;
        }
    }

    return {
        timeRecords,
        start,
        end,
        filteredRecords,
        getTimeRecords,
        saveTimeRecord,
        updateTimeRecord,
        deleteTimeRecord,
    }
});
