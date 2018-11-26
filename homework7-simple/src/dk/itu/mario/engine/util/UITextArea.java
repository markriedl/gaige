package dk.itu.mario.engine.util;

import java.awt.Color;
import java.awt.Font;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.geom.Rectangle2D;
import java.util.ArrayList;

public class UITextArea extends UIItem{

	protected String text;
	protected int width, height;
	protected Font font;
	protected ArrayList<String> lines = new ArrayList<String>();

	public static boolean showBox = false;

	public UITextArea(String text, Font font, int x, int y, int width){
		this.text = text;
		this.font = font;
		this.x = x;
		this.y = y;
		this.width = width;
	}

	public void next() {
	}

	public void prev() {
	}

	public void render(Graphics g) {
		Graphics2D g2 = (Graphics2D)g;

		g.setFont(font);

		lines.clear();

		Rectangle2D rec = font.getStringBounds(text,g2.getFontRenderContext());

		String tempText = new String();

		if(rec.getWidth()>width){
			for(int i=0;i<text.length();++i){
				tempText += text.charAt(i);

				rec = font.getStringBounds(tempText+"A",g2.getFontRenderContext());

				if(rec.getWidth()>=width){
					lines.add(tempText);
					tempText = new String();
				}
			}

			lines.add(tempText);
		}
		else{
			lines.add(text);
		}

		for(int j=0;j<lines.size();++j){
			rec = font.getStringBounds(lines.get(j),g2.getFontRenderContext());
			g.drawString(lines.get(j),x,y+(int)rec.getHeight()*(j+1));
		}

		if(showBox){
			height = (int)rec.getHeight()*lines.size();
			g.setColor(Color.BLUE);
			g.drawRect(x,y,width,height);
		}
	}

	public int getWidth(){
		return width;
	}

	public int getHeight(){
		return height;
	}


}
