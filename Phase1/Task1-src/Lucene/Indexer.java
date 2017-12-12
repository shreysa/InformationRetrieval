
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;

import org.apache.lucene.analysis.core.SimpleAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.StringField;
import org.apache.lucene.document.TextField;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.util.Version;

// class to create a lucene indexer
public class Indexer {
	
	private IndexWriter writer; 
	private ArrayList<File> queue;
	
	//Constructor
	public Indexer(String indexPath) throws IOException
	{
		Directory indexDir = FSDirectory.open(new File(indexPath));
		IndexWriterConfig config = new IndexWriterConfig(Version.LUCENE_47,
				new SimpleAnalyzer(Version.LUCENE_47));
		
		writer = new IndexWriter(indexDir , config);
		queue = new ArrayList<File>();
	}
	
	public void indexFiles(String file) throws IOException
	{
		// gets the list of files in a folder (if user has submitted
		// the name of a folder) or gets a single file name (is user
		// has submitted only the file name)
		getFiles(new File(file));
		
		for(File f : queue) 
		{
			try {
				getDocs(f);
			}
			catch(Exception e) {
				System.out.println("Error indexing " + f + " : "
						+ e.getMessage());
			}
		}
		//Close the index
		writer.close();
	}
	
	//Function to add contents of files to the document
	private void getDocs(File file) throws IOException
	{
		Document doc = new Document();
		FileReader fr = new FileReader(file);
		
		doc.add(new TextField("contents" , fr));
		doc.add(new StringField("path", file.getCanonicalPath(), Field.Store.YES));
		doc.add(new StringField("filename", file.getName(), Field.Store.YES));
		
		//Add document to the index
		writer.addDocument(doc);
		System.out.println("Added: " + file);
	}
	
	//Function to get the file or the files in the directory given
	private void getFiles(File file)
	{
		if (!file.exists()) {
			System.out.println(file + " does not exist.");
		}
		if (file.isDirectory()) {
			for (File f : file.listFiles()) {
				getFiles(f);
			}
		} else {
			String filename = file.getName().toLowerCase();
			//Only index files in the specified file formats
			if (filename.endsWith(".htm") || filename.endsWith(".html")
					|| filename.endsWith(".xml") || filename.endsWith(".txt")) {
				queue.add(file);
			} else {
				System.out.println("Skipped " + filename);
			}
		}
	}
}
