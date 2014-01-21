package com.yovisto.lookas.core.util;

import java.io.InputStream;

import org.apache.log4j.Logger;

/**
 * This class provides a service to execute external command line tools.
 */
public class Commandline {

	private Logger logger = null;

	private StringBuffer cmdOutput = null;
	private StringBuffer cmdError = null;
	private ProcessStreamReader cmdOutputThread = null;
	private ProcessStreamReader cmdErrorThread = null;

	/**
	 * Execute a command.
	 * 
	 * @param cmd
	 *            the cmd
	 * @param verbose
	 *            the verbose
	 * @return the commandline result
	 * @return
	 */
	public CommandlineResult execute(String cmd, boolean verbose, Logger logger) {
		CommandlineResult res = new CommandlineResult(false, -1);
		long duration = 0;
		Process proc = null;

		try {
			if (logger != null)
				logger.debug("Executing command line: " + cmd);

			long start = System.currentTimeMillis();

			/* run command */
			proc = Runtime.getRuntime().exec(cmd);

			/* start output and error read threads */
			startOutputAndErrorReadThreads(proc.getInputStream(), proc.getErrorStream(), verbose);

			if (proc.waitFor() == 0) {
				if (logger != null)
					logger.debug("Execution successful");
				duration = System.currentTimeMillis() - start;
				res.success = true;
				res.duration = duration;

				return res;
			}
		} catch (Exception e) {
			logger.warn("Exception occured at command execution: " + e.getMessage());
			res.success = false;
			res.failureCause = e;
			return res;
		} finally {
			notifyOutputAndErrorReadThreadsToStopReading();
			if (proc != null)
				proc.destroy();
		}
		return res;
	}

	public String getCommandOutput() {
		return cmdOutput.toString();
	}

	public String getCommandError() {
		return cmdError.toString();
	}

	private void startOutputAndErrorReadThreads(InputStream processOut, InputStream processErr, boolean verbose) {
		this.cmdOutput = new StringBuffer();
		this.cmdOutputThread = new ProcessStreamReader(processOut, cmdOutput, logger);
		this.cmdOutputThread.setVerbose(verbose);
		this.cmdOutputThread.start();

		this.cmdError = new StringBuffer();
		this.cmdErrorThread = new ProcessStreamReader(processErr, cmdError, logger);
		this.cmdErrorThread.setVerbose(false);
		this.cmdErrorThread.start();
	}

	private void notifyOutputAndErrorReadThreadsToStopReading() {
		this.cmdOutputThread.stopReading();
		this.cmdErrorThread.stopReading();
	}

}
