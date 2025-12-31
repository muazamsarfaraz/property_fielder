/**
 * Job Detail Page Object
 * 
 * Page object for Flutter mobile app job detail screen.
 */

import { Page, Locator } from '@playwright/test';
import { FlutterBasePage } from './flutter-base.page';
import { FlutterRoutes } from '../config/flutter-config';

export class JobDetailPage extends FlutterBasePage {
  constructor(page: Page) {
    super(page);
  }

  /**
   * Navigate to job detail (requires job ID)
   */
  async goto(jobId?: string): Promise<void> {
    const route = jobId ? `${FlutterRoutes.jobDetail}/${jobId}` : FlutterRoutes.jobDetail;
    await this.navigateTo(route);
  }

  // Main action buttons
  get checkInButton(): Locator {
    return this.page.locator(this.selectors.jobDetail.checkInButton).first();
  }

  get checkOutButton(): Locator {
    return this.page.locator(this.selectors.jobDetail.checkOutButton).first();
  }

  get startInspectionButton(): Locator {
    return this.page.locator(this.selectors.jobDetail.startInspectionButton).first();
  }

  get photoButton(): Locator {
    return this.page.locator(this.selectors.jobDetail.photoButton).first();
  }

  get signatureButton(): Locator {
    return this.page.locator(this.selectors.jobDetail.signatureButton).first();
  }

  get notesButton(): Locator {
    return this.page.locator(this.selectors.jobDetail.notesButton).first();
  }

  /**
   * Check in to job
   */
  async checkIn(): Promise<void> {
    await this.checkInButton.click();
    await this.waitForFlutterReady();
  }

  /**
   * Check out from job
   */
  async checkOut(): Promise<void> {
    await this.checkOutButton.click();
    await this.waitForFlutterReady();
  }

  /**
   * Start inspection
   */
  async startInspection(): Promise<void> {
    await this.startInspectionButton.click();
    await this.waitForRoute(FlutterRoutes.templateExecution);
  }

  /**
   * Open photo capture
   */
  async openPhotoCapture(): Promise<void> {
    await this.photoButton.click();
    await this.waitForFlutterReady();
  }

  /**
   * Open signature capture
   */
  async openSignatureCapture(): Promise<void> {
    await this.signatureButton.click();
    await this.waitForRoute(FlutterRoutes.signatureCapture);
  }

  /**
   * Open notes
   */
  async openNotes(): Promise<void> {
    await this.notesButton.click();
    await this.waitForFlutterReady();
  }

  /**
   * Get property name
   */
  async getPropertyName(): Promise<string> {
    const el = this.page.locator(this.selectors.jobDetail.propertyName);
    return await el.textContent() || '';
  }

  /**
   * Check if checked in
   */
  async isCheckedIn(): Promise<boolean> {
    const checkOutVisible = await this.checkOutButton.isVisible().catch(() => false);
    const checkInHidden = !(await this.checkInButton.isVisible().catch(() => true));
    return checkOutVisible || checkInHidden;
  }

  /**
   * Get all available action buttons
   */
  async getAvailableActions(): Promise<string[]> {
    const actions: string[] = [];
    
    if (await this.checkInButton.isVisible().catch(() => false)) actions.push('Check In');
    if (await this.checkOutButton.isVisible().catch(() => false)) actions.push('Check Out');
    if (await this.startInspectionButton.isVisible().catch(() => false)) actions.push('Start Inspection');
    if (await this.photoButton.isVisible().catch(() => false)) actions.push('Photo');
    if (await this.signatureButton.isVisible().catch(() => false)) actions.push('Signature');
    if (await this.notesButton.isVisible().catch(() => false)) actions.push('Notes');
    
    return actions;
  }

  /**
   * Verify job detail UX elements
   */
  async verifyUXElements(): Promise<{
    hasAppBar: boolean;
    hasPropertyInfo: boolean;
    hasCheckInButton: boolean;
    hasPhotoButton: boolean;
    hasSignatureButton: boolean;
    hasNotesButton: boolean;
    hasMapSection: boolean;
    actionButtons: string[];
  }> {
    const actionButtons = await this.getAvailableActions();
    
    return {
      hasAppBar: await this.page.locator(this.selectors.nav.appBar).isVisible().catch(() => false),
      hasPropertyInfo: await this.page.locator(this.selectors.jobDetail.propertyName).isVisible().catch(() => false),
      hasCheckInButton: await this.checkInButton.isVisible().catch(() => false),
      hasPhotoButton: await this.photoButton.isVisible().catch(() => false),
      hasSignatureButton: await this.signatureButton.isVisible().catch(() => false),
      hasNotesButton: await this.notesButton.isVisible().catch(() => false),
      hasMapSection: await this.page.locator('[aria-label*="map" i], .map-container').isVisible().catch(() => false),
      actionButtons,
    };
  }
}

export default JobDetailPage;

