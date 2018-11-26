package dk.itu.mario.engine.util;

import java.io.BufferedReader;
import java.io.FileReader;

public class FileHandler {

	public static String readFile(String fileName){
		String info = "";
		try {
			FileReader input = new FileReader(fileName);
			BufferedReader bufRead = new BufferedReader(input);
			
            String line; 
            
            int count = 0;	
            line = bufRead.readLine();
            info = line +"\n";
            count++;
            
			
            while (line != null){
//                System.out.println(count+": "+line);
                line = bufRead.readLine();
                info += line + "\n";
                count++;
            }
            
            bufRead.close();
			
        }catch (Exception e){
			// If another exception is generated, print a stack trace
            e.printStackTrace();
        }
        return info;
	}
}
