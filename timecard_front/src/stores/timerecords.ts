import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '@/api/axios';
import type { TimeRecord, RecordAttribute } from '@/types';

const SESSION_STORAGE_START_KEY = 'timecard_date_range_start';
const SESSION_STORAGE_END_KEY = 'timecard_date_range_end';

// Helper to get default dates
const getDefaultStartDate = (): Date => {
    const date = new Date(new Date().getTime() - (14 * 24 * 60 * 60 * 1000));
    date.setHours(0, 0, 0, 0);
    return date;
};

const getDefaultEndDate = (): Date => {
    const date = new Date();
    date.setHours(23, 59, 59, 999);
    return date;
};

// Try to load dates from sessionStorage, fallback to defaults
const loadStoredDate = (key: string, defaultDate: Date): Date => {
    const stored = sessionStorage.getItem(key);
    if (stored) {
        try {
            const date = new Date(stored);
            if (!isNaN(date.getTime())) {
                return date;
            }
        } catch (e) {
            console.warn('Failed to parse stored date:', e);
        }
    }
    return defaultDate;
};

// Initialize cache boundaries with sessionStorage values
const initialStartDate = loadStoredDate(SESSION_STORAGE_START_KEY, getDefaultStartDate());
const initialEndDate = loadStoredDate(SESSION_STORAGE_END_KEY, getDefaultEndDate());
let currentStart = new Date(initialStartDate);
let currentEnd = new Date(initialEndDate);

export const useTimeRecordsStore = defineStore('timerecords', () => {
    const timeRecords = ref<TimeRecord[]>([]);

    // Initialize dates from sessionStorage or defaults
    const startDate = initialStartDate;
    const endDate = initialEndDate;

    const start = ref<Date>(startDate);
    const end = ref<Date>(endDate);
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
            
            // Update the cache boundaries to reflect what we've fetched
            if (start && start < currentStart) {
                currentStart = start;
            }
            if (end && end > currentEnd) {
                currentEnd = end;
            }
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

    const updateDateRange = async (newStart: Date, newEnd: Date) => {
        start.value = newStart;
        end.value = newEnd;
        
        // Persist to sessionStorage
        sessionStorage.setItem(SESSION_STORAGE_START_KEY, newStart.toISOString());
        sessionStorage.setItem(SESSION_STORAGE_END_KEY, newEnd.toISOString());
        
        await getTimeRecords(true, newStart, newEnd);
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
        updateDateRange,
    }
});
