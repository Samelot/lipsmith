// See: http://esotericsoftware.com/forum/Spine-Plugin-in-Support-5859

import java.io.*;
import java.net.Socket;

import javax.sound.sampled.*;

public class Play {
	static public void main (String[] args) throws Exception {
		if (args.length != 2) {
			System.out.println("Usage: java -jar Play [port] [filename]");
			return;
		}

		final Socket socket = new Socket("localhost", Integer.parseInt(args[0]));

		File file = new File(args[1]);
		if (!file.exists()) throw new RuntimeException("File not found: " + file.getAbsolutePath());

		final Clip clip = AudioSystem.getClip();
		clip.open(AudioSystem.getAudioInputStream(new BufferedInputStream(new FileInputStream(file))));

		new Thread() {
			public void run () {
				try {
					BufferedReader input = new BufferedReader(new InputStreamReader(socket.getInputStream()));
					while (true) {
						String line = input.readLine();
						if (line == null) break;
						if (line.startsWith("play ")) {
							clip.setMicrosecondPosition((long)(Float.parseFloat(line.substring(5)) * 1e6f));
							clip.start();
						} else if (line.equals("stop")) clip.stop();
						System.out.println(line);
					}
				} catch (Throwable ex) {
					throw new RuntimeException(ex);
				}
			}
		}.start();

		new Thread() {
			public void run () {
				try {
					OutputStreamWriter output = new OutputStreamWriter(socket.getOutputStream());
					while (true) {
						Thread.sleep(1000 / 60);
						if (clip.isRunning()) {
							output.write("time " + clip.getMicrosecondPosition() / 1e6f + "\n");
							output.flush();
						}
					}
				} catch (Throwable ex) {
					throw new RuntimeException(ex);
				}
			}
		}.start();
	}
}
