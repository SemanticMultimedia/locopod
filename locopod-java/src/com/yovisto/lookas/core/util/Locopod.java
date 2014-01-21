package com.yovisto.lookas.core.util;

import java.io.File;
import java.net.URL;
import java.util.MissingResourceException;

import org.apache.log4j.Logger;

/**
 * Locopod - local copy on demand java wrapper
 * 
 * Using the rsync demon configuration ("/" on external machine is configured as "root").
 * 
 * @author magnus
 */
public class Locopod {

	/**
	 * Request the local path to a file from external server.
	 * 
	 * @param baseFile path to file on external server
	 * @param baseArchive path to archive on external server, (not used, is "/")
	 * @param server external server name
	 * @param logger
	 * @return local path to file
	 */
	public static String getBasePath(String baseFile, String baseArchive, String server, Logger logger) {
		String uri = server + "::root" + baseFile;
		
		return getBasePath(uri, logger);
	}
		
	/**
	 * Request the local path to a file from external server.
	 * 
	 * @param uri uri of file on external server
	 * @param logger
	 * @return local path to file
	 */
	private static String getBasePath(String uri, Logger logger) {
		String basepath = runLocopod("-q -b " + uri, logger); 
		
		File basepathF = new File(basepath);
		if (!basepathF.exists()) {
			basepathF.mkdirs();
		}
		
		return basepath;
	}
		
	/**
	 * Gets a file from external server.
	 * 
	 * @param baseFile path to file on external server
	 * @param baseArchive path to archive on external server, (not used, is "/")
	 * @param server external server name
	 * @param logger
	 * @return local path to file
	 */
	public static String getFileFromRemoteHost(String baseFile, String baseArchive, String server, Logger logger) {
		String uri = server + "::root" + baseFile;
		
		return getFileFromRemoteHost(uri, logger);
	}
	
	/**
	 * Gets a file from external server.
	 * 
	 * @param uri uri of file on external server
	 * @param logger
	 * @return local path to file
	 */
	public static String getFileFromRemoteHost(String uri, Logger logger) {
		return runLocopod("-q -u " + uri, logger);
	}
	
	/**
	 * @param uri
	 * @param logger
	 * @return
	 */
	public static String uploadFileToRemoteHost(String uri, Logger logger) {
		return runLocopod("-q -u " + uri, logger);
	}
	
	/**
	 * @param args
	 * @param logger
	 * @return
	 */
	private static String runLocopod(String args, Logger logger) {
		Commandline cmdLine = new Commandline();
		
		String cmd = "python " + getLocopodPath() + " " + args;
		
		CommandlineResult res = cmdLine.execute(cmd, false, logger);
		
		return cmdLine.getCommandOutput().trim();
	}
	
	/**
	 * @return
	 * @throws MissingResourceException
	 */
	private static String getLocopodPath() throws MissingResourceException {

		File local = new File("/usr/local/locopod/locopod.py");
		if (local.exists()) {
			return local.getAbsolutePath();
		}	
		
		URL script = Locopod.class.getResource("/locopod/locopod.py");
		
		if (script == null) {
			throw new MissingResourceException("Cannot locate 'locopod.py'.", Locopod.class.getCanonicalName(), "locopod.py");
		}
		
		return script.getPath();
	}
}
