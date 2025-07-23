from typing import List, Optional, Dict
from pydantic import BaseModel

class SessionsAttended(BaseModel):
    total: str
    attended: str
    committee_total: str
    committee_attended: str
    ldpr_total: str
    ldpr_attended: str

class GeneralInfo(BaseModel):
    full_name: str
    district: str
    term_start: str
    term_end: str
    links: List[str]
    position: str
    committees: List[str]
    sessions_attended: SessionsAttended
    region: str
    authority_name: str
    ldpr_position: Optional[str] = None  # Добавлено, так как присутствует в JSON

class Legislation(BaseModel):
    title: str
    summary: str
    status: str
    rejection_reason: Optional[str] = None
    links: List[str] = []  # Добавлено, так как присутствует в JSON

class Requests(BaseModel):
    utilities: str
    pensions_and_social_payments: str
    improvement: str
    education: str
    svo: str
    road_maintenance: str
    ecology: str
    medicine_and_healthcare: str
    public_transport: str
    illegal_dumps: str
    appeals_to_ldpr_chairman: str
    legal_aid_requests: str
    integrated_territory_development: str
    stray_animal_issues: str
    legislative_proposals: str

class Example(BaseModel):
    text: str
    links: List[str] = []  # Добавлено, так как присутствует в JSON

class CitizenRequests(BaseModel):
    personal_meetings: str
    requests: Requests
    responses: str
    official_queries: str
    examples: List[Example]
    total_requests: str

class SVOSupportProject(BaseModel):
    name: Optional[str] = None  # Может быть пустым, как в JSON
    links: List[str] = []      # Добавлено, так как присутствует в JSON
    text: Optional[str] = None  # Добавлено, так как присутствует в JSON

class SVOSupport(BaseModel):
    projects: List[SVOSupportProject]

class ProjectActivity(BaseModel):
    name: str
    result: str

class LDPROrders(BaseModel):
    instruction: str
    action: str

class LDPRReport(BaseModel):
    general_info: GeneralInfo
    legislation: List[Legislation]
    citizen_requests: CitizenRequests
    svo_support: SVOSupport
    project_activity: List[ProjectActivity]
    ldpr_orders: List[LDPROrders]
    other_info: Optional[str] = None  # Добавлено, так как присутствует в JSON
