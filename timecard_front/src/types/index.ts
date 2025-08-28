
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
  domain_id: number
  category_id: number
  title_id: number
  timein: string
  timeout: string | null
}
