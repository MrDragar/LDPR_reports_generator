
export interface GeneralInfo {
  full_name: string;
  district: string;
  term_start: string;
  term_end: string;
  links: string[];
  position: string;
  committees: string[];
  sessions_attended: {
    total: string;
    attended: string;
    committee_total: string;
    committee_attended: string;
    ldpr_total: string;
    ldpr_attended: string;
  };
}

export interface Legislation {
  title: string;
  summary: string;
  status: string;
  rejection_reason: string;
}

export interface CitizenRequests {
  personal_meetings: string;
  requests: { [key: string]: string };
  responses: string;
  official_queries: string;
  examples: string[];
}

export interface SvoSupport {
  projects: string[];
}

export interface ProjectActivity {
  name: string;
  result: string;
}

export interface LdprOrder {
  instruction: string;
  action: string;
}

export interface ReportFormData {
  general_info: GeneralInfo;
  legislation: Legislation[];
  citizen_requests: CitizenRequests;
  svo_support: SvoSupport;
  project_activity: ProjectActivity[];
  ldpr_orders: LdprOrder[];
  other_info: string;
}
