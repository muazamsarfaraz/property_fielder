/**
 * User Stories for Flutter Mobile App Testing
 * 
 * Complete user story definitions with acceptance criteria
 * for Property Fielder Inspector Mobile App.
 */

export interface UserStory {
  id: string;
  name: string;
  description: string;
  actor: 'Inspector' | 'Supervisor' | 'System';
  priority: 'Critical' | 'High' | 'Medium' | 'Low';
  steps: string[];
  acceptanceCriteria: string[];
  screens: string[];
  tags: string[];
}

export const UserStories: Record<string, UserStory> = {
  // Authentication Stories
  inspectorLogin: {
    id: 'US-AUTH-001',
    name: 'Inspector Login',
    description: 'As an inspector, I can log into the mobile app to access my assigned jobs',
    actor: 'Inspector',
    priority: 'Critical',
    steps: [
      'Open the mobile app',
      'Enter email/username',
      'Enter password',
      'Tap Login button',
      'Wait for authentication',
      'See dashboard with job summary',
    ],
    acceptanceCriteria: [
      'Login form is visible with email and password fields',
      'Login button is enabled when both fields are filled',
      'Loading indicator shown during authentication',
      'Dashboard loads after successful login',
      'Error message shown for invalid credentials',
      'Session persists after app restart',
    ],
    screens: ['/login', '/dashboard'],
    tags: ['auth', 'critical', 'smoke'],
  },

  // Job Management Stories
  viewAssignedJobs: {
    id: 'US-JOB-001',
    name: 'View Assigned Jobs',
    description: 'As an inspector, I can view my assigned jobs for today',
    actor: 'Inspector',
    priority: 'Critical',
    steps: [
      'Navigate to Jobs screen',
      'See list of assigned jobs',
      'View job count and status summary',
      'Filter jobs by status',
      'Search for specific property',
    ],
    acceptanceCriteria: [
      'Job list loads with all assigned jobs',
      'Each job shows property name, address, time',
      'Filter chips for Pending/In Progress/Completed',
      'Search filters jobs in real-time',
      'Pull-to-refresh updates job list',
    ],
    screens: ['/jobs'],
    tags: ['jobs', 'critical', 'smoke'],
  },

  jobCheckInOut: {
    id: 'US-JOB-002',
    name: 'Job Check-In/Check-Out',
    description: 'As an inspector, I can check in and out of a job with GPS verification',
    actor: 'Inspector',
    priority: 'Critical',
    steps: [
      'Open job details',
      'Tap Check In button',
      'Allow GPS location access',
      'Confirm check-in with current location',
      'Perform inspection work',
      'Tap Check Out button',
      'Confirm check-out',
    ],
    acceptanceCriteria: [
      'Check In button visible on job detail',
      'GPS location captured on check-in',
      'Timestamp recorded for check-in',
      'Job status changes to In Progress',
      'Check Out button appears after check-in',
      'Duration calculated on check-out',
    ],
    screens: ['/jobs/detail'],
    tags: ['jobs', 'gps', 'critical'],
  },

  // Evidence Capture Stories
  capturePhotos: {
    id: 'US-PHOTO-001',
    name: 'Capture Inspection Photos',
    description: 'As an inspector, I can take photos during an inspection',
    actor: 'Inspector',
    priority: 'High',
    steps: [
      'Open job details',
      'Tap Photo button',
      'Camera opens',
      'Take photo',
      'Add caption/category',
      'Save photo',
      'View in gallery',
    ],
    acceptanceCriteria: [
      'Camera opens when Photo button tapped',
      'Photo preview shown after capture',
      'Category selection available (Before/After/Defect)',
      'GPS location tagged to photo',
      'Photos saved locally for offline',
      'Photos sync when online',
    ],
    screens: ['/jobs/detail', '/photos'],
    tags: ['photos', 'evidence', 'high'],
  },

  captureSignature: {
    id: 'US-SIG-001',
    name: 'Capture Signature',
    description: 'As an inspector, I can capture tenant/owner signature',
    actor: 'Inspector',
    priority: 'High',
    steps: [
      'Open job details',
      'Tap Signature button',
      'Signature pad opens',
      'Collect signature',
      'Enter signatory name',
      'Save signature',
    ],
    acceptanceCriteria: [
      'Signature pad opens full-screen',
      'Clear button to reset signature',
      'Signatory name field required',
      'Timestamp captured with signature',
      'Signature saved as image',
    ],
    screens: ['/signature'],
    tags: ['signature', 'evidence', 'high'],
  },

  // Safety Stories
  safetyTimerWorkflow: {
    id: 'US-SAFETY-001',
    name: 'Safety Timer (Lone Worker)',
    description: 'As a lone worker inspector, I can start a safety timer for HSE compliance',
    actor: 'Inspector',
    priority: 'Critical',
    steps: [
      'Navigate to Safety Timer',
      'Select duration (30/60/90/120 min)',
      'Tap Start Timer',
      'Timer countdown begins',
      'Extend timer if needed',
      'Complete timer when safe',
    ],
    acceptanceCriteria: [
      'Duration options clearly visible',
      'Large countdown display',
      'Extend button adds 30 minutes',
      'Complete button confirms safety',
      'Overdue state shows warning',
      'GPS location captured on start',
    ],
    screens: ['/safety'],
    tags: ['safety', 'hse', 'critical'],
  },

  panicButton: {
    id: 'US-SAFETY-002',
    name: 'Panic Button Emergency',
    description: 'As an inspector in danger, I can trigger a panic alert',
    actor: 'Inspector',
    priority: 'Critical',
    steps: [
      'Long-press Panic button',
      'Confirmation dialog appears',
      'Optionally enter reason',
      'Confirm panic alert',
      'GPS location sent',
      'Emergency contacts notified',
    ],
    acceptanceCriteria: [
      'Panic button prominently visible (red)',
      'Long-press required to prevent accidents',
      'Confirmation dialog prevents false alarms',
      'GPS location included in alert',
      'Haptic feedback on activation',
      'Confirmation shown after alert sent',
    ],
    screens: ['/safety'],
    tags: ['safety', 'panic', 'critical'],
  },

  // Inspection Template Stories
  executeInspectionTemplate: {
    id: 'US-TEMPLATE-001',
    name: 'Execute Inspection Template',
    description: 'As an inspector, I can complete a structured inspection checklist',
    actor: 'Inspector',
    priority: 'High',
    steps: [
      'Start inspection from job',
      'Template loads with sections',
      'Navigate through sections',
      'Answer checklist items',
      'Add notes where needed',
      'Submit completed inspection',
    ],
    acceptanceCriteria: [
      'Template sections shown as progress indicators',
      'Checklist items display with response options',
      'Yes/No/N/A buttons for boolean items',
      'Severity chips for defect items',
      'Notes can be added to any item',
      'Progress percentage updates in real-time',
      'Submit validates mandatory items',
    ],
    screens: ['/inspection/execute'],
    tags: ['inspection', 'template', 'high'],
  },
};

export default UserStories;

