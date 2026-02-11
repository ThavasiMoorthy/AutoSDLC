export interface ProjectBrief {
    name: string;
    description: string;
    brief_content: string;
}

export interface Requirement {
    id: string;
    description: string;
    priority: "High" | "Medium" | "Low";
    acceptance_criteria: string[];
}

export interface SRS {
    project_id: string;
    requirements: Requirement[];
    generated_at: string;
}

export interface WBSTask {
    id: string;
    name: string;
    description: string;
    estimated_days: number;
    dependencies: string[];
    assigned_role?: string;
}

export interface ProjectPlan {
    project_id: string;
    tasks: WBSTask[];
    total_estimated_days: number;
    estimated_cost: number;
}

export interface AgentStatus {
    agent_name: string;
    status: "idle" | "working" | "completed" | "failed";
    current_task?: string;
    last_updated: string;
}

export interface Artifacts {
    file_structure: string[];
    code_snippets: Record<string, string>;
}

export interface ProjectState {
    id: string;
    brief: ProjectBrief;
    srs?: SRS;
    plan?: ProjectPlan;
    artifacts?: Artifacts;
    status: string;
    agent_statuses: Record<string, AgentStatus>;
}
