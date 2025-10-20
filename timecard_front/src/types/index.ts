
export interface RecordAttribute {
  id?: number
  name: string
  parent_id: number | null
  user_id: number
  level_num: number
  color: string | null
}

export interface TimeRecord {
  id?: number
  domain_id: number | string
  category_id: number | string
  title_id: number | string
  timein: string | Date
  timeout: string | Date | null
  external_link: string | null
  notes: string | null
}

export type CategoryRecord = {
  timeDiff: number;
  category_id: number | string;
}

export type SummaryData = {
  domainId: number | string;
  totalTime: number;
  categoryRecords: CategoryRecord[];
}
