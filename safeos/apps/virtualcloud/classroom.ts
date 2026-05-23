export interface ClassroomSession {
  className: string;
  studentCount: number;
}

export function summarizeSession(session: ClassroomSession) {
  return `${session.className}: ${session.studentCount} students`;
}
