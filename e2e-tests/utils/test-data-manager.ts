import { Page } from '@playwright/test';
import { OdooHelpers } from './odoo-helpers';

/**
 * Manages test data creation and cleanup
 * All data is created on-demand and tracked for cleanup
 */
export class TestDataManager {
  private odoo: OdooHelpers;
  private createdRecords: Map<string, number[]> = new Map();

  constructor(private page: Page) {
    this.odoo = new OdooHelpers(page);
  }

  /**
   * Track a created record for later cleanup
   */
  trackRecord(model: string, id: number): void {
    if (!this.createdRecords.has(model)) {
      this.createdRecords.set(model, []);
    }
    this.createdRecords.get(model)!.push(id);
  }

  /**
   * Get all created record IDs for a model
   */
  getCreatedRecords(model: string): number[] {
    return this.createdRecords.get(model) || [];
  }

  /**
   * Clear tracking (does not delete records)
   */
  clearTracking(): void {
    this.createdRecords.clear();
  }

  /**
   * Generate a unique test identifier
   */
  static uniqueId(prefix: string = 'TEST'): string {
    return `${prefix}_${Date.now()}_${Math.random().toString(36).substring(7)}`;
  }

  /**
   * Generate test property data
   */
  static propertyData(overrides: Partial<PropertyData> = {}): PropertyData {
    const id = this.uniqueId('PROP');
    return {
      name: `Test Property ${id}`,
      street: `${Math.floor(Math.random() * 9999)} Test Street`,
      city: 'Test City',
      state: 'NSW',
      postcode: '2000',
      country: 'Australia',
      property_type: 'residential',
      ...overrides,
    };
  }

  /**
   * Generate test job data
   */
  static jobData(overrides: Partial<JobData> = {}): JobData {
    const id = this.uniqueId('JOB');
    return {
      name: `Test Job ${id}`,
      scheduled_date: new Date().toISOString().split('T')[0],
      duration_minutes: 60,
      priority: 'medium',
      ...overrides,
    };
  }

  /**
   * Generate test inspector data
   */
  static inspectorData(overrides: Partial<InspectorData> = {}): InspectorData {
    const id = this.uniqueId('INSP');
    return {
      name: `Test Inspector ${id}`,
      email: `inspector_${id.toLowerCase()}@test.com`,
      available: true,
      ...overrides,
    };
  }

  /**
   * Generate test route data
   */
  static routeData(overrides: Partial<RouteData> = {}): RouteData {
    const id = this.uniqueId('ROUTE');
    return {
      name: `Test Route ${id}`,
      route_date: new Date().toISOString().split('T')[0],
      ...overrides,
    };
  }

  /**
   * Generate test certification type data
   */
  static certificationTypeData(overrides: Partial<CertificationTypeData> = {}): CertificationTypeData {
    const id = this.uniqueId('CERT');
    return {
      name: `Test Certification ${id}`,
      code: id,
      validity_months: 12,
      ...overrides,
    };
  }
}

// Type definitions for test data
export interface PropertyData {
  name: string;
  street: string;
  city: string;
  state: string;
  postcode: string;
  country: string;
  property_type: string;
  partner_id?: number;
  latitude?: number;
  longitude?: number;
}

export interface JobData {
  name: string;
  scheduled_date: string;
  duration_minutes: number;
  priority: string;
  property_id?: number;
  inspector_id?: number;
}

export interface InspectorData {
  name: string;
  email: string;
  available: boolean;
  user_id?: number;
}

export interface RouteData {
  name: string;
  route_date: string;
  inspector_id?: number;
}

export interface CertificationTypeData {
  name: string;
  code: string;
  validity_months: number;
}

