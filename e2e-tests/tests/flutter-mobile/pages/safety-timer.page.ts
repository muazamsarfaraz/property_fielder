/**
 * Safety Timer Page Object
 * 
 * Page object for Flutter mobile app safety timer (lone worker protection) screen.
 */

import { Page, Locator } from '@playwright/test';
import { FlutterBasePage } from './flutter-base.page';
import { FlutterRoutes } from '../config/flutter-config';

export type TimerDuration = 30 | 60 | 90 | 120;

export class SafetyTimerPage extends FlutterBasePage {
  constructor(page: Page) {
    super(page);
  }

  /**
   * Navigate to safety timer
   */
  async goto(): Promise<void> {
    await this.navigateTo(FlutterRoutes.safetyTimer);
  }

  // Elements
  get timerDisplay(): Locator {
    return this.page.locator(this.selectors.safetyTimer.timerDisplay);
  }

  get startButton(): Locator {
    return this.page.locator(this.selectors.safetyTimer.startButton).first();
  }

  get extendButton(): Locator {
    return this.page.locator(this.selectors.safetyTimer.extendButton).first();
  }

  get cancelButton(): Locator {
    return this.page.locator(this.selectors.safetyTimer.cancelButton).first();
  }

  get panicButton(): Locator {
    return this.page.locator(this.selectors.safetyTimer.panicButton).first();
  }

  get durationChips(): Locator {
    return this.page.locator(this.selectors.safetyTimer.durationChip);
  }

  /**
   * Select timer duration
   */
  async selectDuration(minutes: TimerDuration): Promise<void> {
    const chip = this.page.locator(`[role="radio"]:has-text("${minutes}")`).first();
    if (await chip.isVisible()) {
      await chip.click();
    } else {
      // Try button variant
      await this.page.getByRole('button', { name: `${minutes}` }).click();
    }
    await this.page.waitForTimeout(this.config.timeouts.animation);
  }

  /**
   * Start the timer
   */
  async startTimer(): Promise<void> {
    await this.startButton.click();
    await this.waitForFlutterReady();
  }

  /**
   * Extend the timer
   */
  async extendTimer(): Promise<void> {
    await this.extendButton.click();
    await this.waitForFlutterReady();
  }

  /**
   * Complete/cancel the timer (mark as safe)
   */
  async completeTimer(): Promise<void> {
    await this.cancelButton.click();
    await this.waitForFlutterReady();
  }

  /**
   * Trigger panic alert (long press simulation)
   */
  async triggerPanic(): Promise<void> {
    const box = await this.panicButton.boundingBox();
    if (box) {
      await this.page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
      await this.page.mouse.down();
      await this.page.waitForTimeout(2000); // Long press duration
      await this.page.mouse.up();
    }
    await this.waitForFlutterReady();
  }

  /**
   * Get current timer display value
   */
  async getTimerValue(): Promise<string> {
    return await this.timerDisplay.textContent() || '00:00';
  }

  /**
   * Check if timer is active
   */
  async isTimerActive(): Promise<boolean> {
    const extendVisible = await this.extendButton.isVisible().catch(() => false);
    const cancelVisible = await this.cancelButton.isVisible().catch(() => false);
    return extendVisible || cancelVisible;
  }

  /**
   * Check if timer is overdue
   */
  async isOverdue(): Promise<boolean> {
    // Look for overdue indicators (red styling, warning text)
    const overdueIndicator = this.page.locator('[aria-label*="overdue" i], .overdue, .warning');
    return await overdueIndicator.isVisible().catch(() => false);
  }

  /**
   * Verify safety timer UX elements
   */
  async verifyUXElements(): Promise<{
    hasAppBar: boolean;
    hasTimerDisplay: boolean;
    hasDurationOptions: boolean;
    hasStartButton: boolean;
    hasPanicButton: boolean;
    isTimerActive: boolean;
    durationCount: number;
  }> {
    const durationCount = await this.durationChips.count();
    const isActive = await this.isTimerActive();
    
    return {
      hasAppBar: await this.page.locator(this.selectors.nav.appBar).isVisible().catch(() => false),
      hasTimerDisplay: await this.timerDisplay.isVisible().catch(() => false),
      hasDurationOptions: durationCount > 0,
      hasStartButton: await this.startButton.isVisible().catch(() => false),
      hasPanicButton: await this.panicButton.isVisible().catch(() => false),
      isTimerActive: isActive,
      durationCount,
    };
  }

  /**
   * Get all available duration options
   */
  async getDurationOptions(): Promise<number[]> {
    const chips = await this.durationChips.allTextContents();
    return chips
      .map(text => parseInt(text.replace(/\D/g, '')))
      .filter(n => !isNaN(n));
  }
}

export default SafetyTimerPage;

