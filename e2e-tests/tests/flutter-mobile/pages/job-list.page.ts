/**
 * Job List Page Object
 * 
 * Page object for Flutter mobile app job list screen.
 */

import { Page, Locator } from '@playwright/test';
import { FlutterBasePage } from './flutter-base.page';
import { FlutterRoutes } from '../config/flutter-config';

export interface JobCardInfo {
  index: number;
  propertyName: string;
  address: string;
  status: string;
  time: string;
}

export class JobListPage extends FlutterBasePage {
  constructor(page: Page) {
    super(page);
  }

  /**
   * Navigate to job list
   */
  async goto(): Promise<void> {
    await this.navigateTo(FlutterRoutes.jobList);
  }

  /**
   * Get job cards
   */
  get jobCards(): Locator {
    return this.page.locator(this.selectors.jobList.jobCard);
  }

  /**
   * Get search input
   */
  get searchInput(): Locator {
    return this.page.locator(this.selectors.jobList.searchInput);
  }

  /**
   * Get filter chips
   */
  get filterChips(): Locator {
    return this.page.locator(this.selectors.jobList.filterChip);
  }

  /**
   * Get refresh button
   */
  get refreshButton(): Locator {
    return this.page.locator(this.selectors.jobList.refreshButton);
  }

  /**
   * Get job count
   */
  async getJobCount(): Promise<number> {
    return await this.jobCards.count();
  }

  /**
   * Search for jobs
   */
  async search(query: string): Promise<void> {
    await this.searchInput.fill(query);
    await this.page.waitForTimeout(500); // Debounce
  }

  /**
   * Clear search
   */
  async clearSearch(): Promise<void> {
    await this.searchInput.clear();
    await this.page.waitForTimeout(500);
  }

  /**
   * Filter by status
   */
  async filterByStatus(status: 'Pending' | 'In Progress' | 'Completed' | 'All'): Promise<void> {
    const chip = this.page.locator(`[role="button"]:has-text("${status}")`).first();
    await chip.click();
    await this.waitForFlutterReady();
  }

  /**
   * Click on a job card by index
   */
  async clickJob(index: number): Promise<void> {
    await this.jobCards.nth(index).click();
    await this.waitForFlutterReady();
  }

  /**
   * Click on a job by property name
   */
  async clickJobByName(propertyName: string): Promise<void> {
    const card = this.page.locator(`${this.selectors.jobList.jobCard}:has-text("${propertyName}")`);
    await card.click();
    await this.waitForFlutterReady();
  }

  /**
   * Refresh job list
   */
  async refresh(): Promise<void> {
    if (await this.refreshButton.isVisible()) {
      await this.refreshButton.click();
    } else {
      // Try pull-to-refresh simulation
      await this.page.mouse.move(200, 200);
      await this.page.mouse.down();
      await this.page.mouse.move(200, 500, { steps: 10 });
      await this.page.mouse.up();
    }
    await this.waitForFlutterReady();
  }

  /**
   * Get job card info
   */
  async getJobInfo(index: number): Promise<Partial<JobCardInfo>> {
    const card = this.jobCards.nth(index);
    const text = await card.textContent();
    
    return {
      index,
      propertyName: text?.split('\n')[0] || '',
    };
  }

  /**
   * Get all job names
   */
  async getAllJobNames(): Promise<string[]> {
    const count = await this.getJobCount();
    const names: string[] = [];
    
    for (let i = 0; i < count; i++) {
      const info = await this.getJobInfo(i);
      if (info.propertyName) {
        names.push(info.propertyName);
      }
    }
    
    return names;
  }

  /**
   * Verify job list UX elements
   */
  async verifyUXElements(): Promise<{
    hasAppBar: boolean;
    hasSearchBar: boolean;
    hasFilterChips: boolean;
    hasJobCards: boolean;
    hasRefresh: boolean;
    jobCount: number;
  }> {
    const jobCount = await this.getJobCount();
    
    return {
      hasAppBar: await this.page.locator(this.selectors.nav.appBar).isVisible().catch(() => false),
      hasSearchBar: await this.searchInput.isVisible().catch(() => false),
      hasFilterChips: await this.filterChips.first().isVisible().catch(() => false),
      hasJobCards: jobCount > 0,
      hasRefresh: await this.refreshButton.isVisible().catch(() => false),
      jobCount,
    };
  }
}

export default JobListPage;

