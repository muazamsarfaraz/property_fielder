/**
 * Dashboard Page Object
 * 
 * Page object for Flutter mobile app dashboard/home screen.
 */

import { Page } from '@playwright/test';
import { FlutterBasePage } from './flutter-base.page';
import { FlutterRoutes } from '../config/flutter-config';

export interface DashboardStats {
  pendingJobs: number;
  inProgressJobs: number;
  completedJobs: number;
  syncPending: number;
}

export class DashboardPage extends FlutterBasePage {
  constructor(page: Page) {
    super(page);
  }

  /**
   * Navigate to dashboard
   */
  async goto(): Promise<void> {
    await this.navigateTo(FlutterRoutes.dashboard);
  }

  /**
   * Get the menu/drawer button
   */
  get menuButton() {
    return this.page.locator(this.selectors.dashboard.menuButton);
  }

  /**
   * Get navigation drawer
   */
  get navigationDrawer() {
    return this.page.locator(this.selectors.dashboard.navigationDrawer);
  }

  /**
   * Open navigation drawer
   */
  async openDrawer(): Promise<void> {
    await this.menuButton.click();
    await this.page.waitForTimeout(this.config.timeouts.animation);
  }

  /**
   * Navigate via drawer menu
   */
  async navigateViaDrawer(menuItem: string): Promise<void> {
    await this.openDrawer();
    await this.page.getByRole('button', { name: menuItem }).click();
    await this.waitForFlutterReady();
  }

  /**
   * Get job statistics from dashboard cards
   */
  async getStats(): Promise<Partial<DashboardStats>> {
    const stats: Partial<DashboardStats> = {};
    
    // Try to find job count elements
    const jobCountEl = this.page.locator(this.selectors.dashboard.jobCount);
    if (await jobCountEl.isVisible({ timeout: 2000 }).catch(() => false)) {
      const text = await jobCountEl.textContent();
      const match = text?.match(/(\d+)/);
      if (match) {
        stats.pendingJobs = parseInt(match[1]);
      }
    }

    return stats;
  }

  /**
   * Check sync status
   */
  async getSyncStatus(): Promise<string> {
    const syncEl = this.page.locator(this.selectors.dashboard.syncStatus);
    if (await syncEl.isVisible({ timeout: 2000 }).catch(() => false)) {
      return await syncEl.textContent() || 'unknown';
    }
    return 'unknown';
  }

  /**
   * Navigate to Jobs list
   */
  async goToJobs(): Promise<void> {
    await this.clickButton('Jobs');
    await this.waitForRoute(FlutterRoutes.jobList);
  }

  /**
   * Navigate to Safety Timer
   */
  async goToSafety(): Promise<void> {
    await this.navigateViaDrawer('Safety');
    await this.waitForRoute(FlutterRoutes.safetyTimer);
  }

  /**
   * Navigate to Settings
   */
  async goToSettings(): Promise<void> {
    await this.navigateViaDrawer('Settings');
    await this.waitForRoute(FlutterRoutes.settings);
  }

  /**
   * Navigate to Sync screen
   */
  async goToSync(): Promise<void> {
    await this.navigateViaDrawer('Sync');
    await this.waitForRoute(FlutterRoutes.sync);
  }

  /**
   * Check if dashboard is loaded
   */
  async isDashboardLoaded(): Promise<boolean> {
    // Check for common dashboard elements
    const hasAppBar = await this.page.locator(this.selectors.nav.appBar).isVisible().catch(() => false);
    const hasContent = await this.page.locator('[role="main"], main, .dashboard').isVisible().catch(() => false);
    return hasAppBar || hasContent;
  }

  /**
   * Verify dashboard UX elements
   */
  async verifyUXElements(): Promise<{
    hasAppBar: boolean;
    hasJobSummary: boolean;
    hasNavigation: boolean;
    hasSyncStatus: boolean;
    hasQuickActions: boolean;
  }> {
    return {
      hasAppBar: await this.page.locator(this.selectors.nav.appBar).isVisible().catch(() => false),
      hasJobSummary: await this.page.locator(this.selectors.dashboard.jobCount).isVisible().catch(() => false),
      hasNavigation: await this.menuButton.isVisible().catch(() => false),
      hasSyncStatus: await this.page.locator(this.selectors.dashboard.syncStatus).isVisible().catch(() => false),
      hasQuickActions: await this.page.locator(this.selectors.nav.fab).isVisible().catch(() => false),
    };
  }

  /**
   * Get all visible action buttons
   */
  async getQuickActions(): Promise<string[]> {
    const buttons = this.page.getByRole('button');
    const count = await buttons.count();
    const actions: string[] = [];
    
    for (let i = 0; i < count; i++) {
      const text = await buttons.nth(i).textContent();
      if (text?.trim()) {
        actions.push(text.trim());
      }
    }
    
    return actions;
  }
}

export default DashboardPage;

