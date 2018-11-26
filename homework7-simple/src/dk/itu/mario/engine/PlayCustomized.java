package dk.itu.mario.engine;

import java.awt.*;

import javax.swing.*;

import java.lang.ArrayIndexOutOfBoundsException;
import dk.itu.mario.engine.DataRecorder;

public class PlayCustomized {

	public static void main(String[] args)
     {
		    	JFrame frame = new JFrame("Mario Experience Showcase");

		    	String playerProfile = "Scrooge";
		    	try{
		    		playerProfile = args[0];
		    		
		    	}
		    	catch (ArrayIndexOutOfBoundsException a){
		    		playerProfile = "Scrooge";
		    	}
		    	
		    	
		    	MarioComponent mario = new MarioComponent(640, 480, playerProfile);

		    	frame.setContentPane(mario);
		    	frame.setResizable(false);
		        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		        frame.pack();

		        Dimension screenSize = Toolkit.getDefaultToolkit().getScreenSize();
		        frame.setLocation((screenSize.width-frame.getWidth())/2, (screenSize.height-frame.getHeight())/2);

		        frame.setVisible(true);

		        mario.start();   
	}	

}
