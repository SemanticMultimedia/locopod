package com.yovisto.lookas.core.util;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;

import org.apache.log4j.Logger;

/**
 * The Class ProcessStreamReader.
 */
public class ProcessStreamReader extends Thread {
	
	private static final Logger L = Logger.getLogger(ProcessStreamReader.class.getName());

	private StringBuffer buffer = null;
	private InputStream inputStream = null;
	private boolean stopIt = false;
	private Logger logger = null;

	private boolean verbose = false;

	private String newLine = null;

	public ProcessStreamReader(InputStream inputStream, StringBuffer buffer,
			Logger logger) {
		this.inputStream = inputStream;
		this.buffer = buffer;
		this.logger = logger;

		this.newLine = System.getProperty("line.separator");
	}

	public String getBuffer() {
		return buffer.toString();
	}

	public boolean isVerbose() {
		return verbose;
	}

	public void setVerbose(boolean verbose) {
		this.verbose = verbose;
	}

	public void run() {
		try {
			readCommandOutput();
		} catch (Exception ex) {
			// ex.printStackTrace(); //DEBUG
		}
	}

	private void readCommandOutput() throws IOException {
		BufferedReader bufOut = new BufferedReader(new InputStreamReader(
				inputStream));
		String line = null;
		while ((stopIt == false) && ((line = bufOut.readLine()) != null)) {
			buffer.append(line + newLine);
			if (this.logger != null)
				this.logger.info(line);
			if (verbose)
				L.info("Command returned: " + line);
		}
		bufOut.close();
	}

	public void stopReading() {
		stopIt = true;
	}

}