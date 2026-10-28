export interface InvestigationEvent { event:string; details:Record<string,unknown>; }
export interface InvestigationResult {
 investigation_id:string; status:string;
 failure?:{summary:string;category:string;failing_tests:string[];error_messages:string[];affected_files:string[]};
 repair_plan?:{root_cause:string;reasoning:string;files_to_change:string[];proposed_changes:string[];risks:string[]};
 changed_files?:string[]; verification?:{passed:boolean;exit_code:number|null;summary:string;failing_tests:string[];duration_seconds:number};
 attempts?:number; events?:InvestigationEvent[]; baseline?:{passed?:boolean;exit_code?:number|null;duration_seconds?:number}; latest_test_output?:string;
}
