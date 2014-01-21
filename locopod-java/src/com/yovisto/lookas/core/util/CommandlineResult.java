package com.yovisto.lookas.core.util;

/**
 * The Class CommandlineResult.
 */
public class CommandlineResult {

	/** The success. */
	public boolean success;

	/** The failure cause. */
	public Object failureCause;

	/** The duration. */
	public long duration;

	/**
	 * Instantiates a new commandline result.
	 * 
	 * @param success the success
	 * @param duration the duration
	 */
	public CommandlineResult(boolean success, long duration) {
		this.success = success;
		this.duration = duration;
	}
}
