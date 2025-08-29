
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
  timein: string
  timeout: string | null
}
