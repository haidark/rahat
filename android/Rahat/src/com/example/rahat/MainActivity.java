package com.example.rahat;

import java.io.BufferedWriter;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.InetAddress;
import java.net.Socket;
import java.net.UnknownHostException;
import java.text.SimpleDateFormat;
import java.util.Date;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.app.AlarmManager;
import android.app.Dialog;
import android.app.DialogFragment;
import android.app.PendingIntent;
import android.app.Service;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentSender;
import android.content.SharedPreferences;
import android.content.SharedPreferences.Editor;
import android.location.Location;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.IBinder;
import android.os.Looper;
import android.os.Message;
import android.os.Process;
import android.os.SystemClock;
import android.provider.Settings.Secure;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentActivity;
import android.support.v7.app.ActionBarActivity;
import android.text.format.Time;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;
import android.widget.ToggleButton;

import com.google.android.gms.common.ConnectionResult;
import com.google.android.gms.common.GooglePlayServicesClient;
import com.google.android.gms.common.GooglePlayServicesUtil;
import com.google.android.gms.location.LocationClient;
import com.google.android.gms.location.LocationListener;
import com.google.android.gms.location.LocationRequest;

@SuppressWarnings("unused")
public class MainActivity extends ActionBarActivity implements
	GooglePlayServicesClient.ConnectionCallbacks,
	GooglePlayServicesClient.OnConnectionFailedListener {
	// Global constants
    /*
     * Define a request code to send to Google Play services
     * This code is returned in Activity.onActivityResult
     */
    private final static int CONNECTION_FAILURE_RESOLUTION_REQUEST = 9000;
    private static final int MILLISECONDS_PER_SECOND = 1000;
    private LocationClient mLocationClient;
	private String dispMsg = "";
	public static String serverName = "haidarkhan.no-ip.org";
	public static String port = "1060";

	//Called on Activity creation
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_main);
		
		// Create a new location client, using the enclosing class to handle callbacks.
        mLocationClient = new LocationClient(this, this, this);
        
		if (savedInstanceState == null) {
			getSupportFragmentManager().beginTransaction()
					.add(R.id.container, new PlaceholderFragment()).commit();
		}
	}
	
	/*
     * Called when the Activity becomes visible.
     */
    @Override
    protected void onStart() {
        super.onStart();
        //check if google play services are installed
      	servicesConnected();
        // Connect the client.
        mLocationClient.connect();        
    }
    
    // Called when Activity is paused
    //called when the Activity is paused
    @Override
    protected void onPause() {
        super.onPause();
    }
    
    //called when the Activity is resumed
    
    // Called on Activity Resuming
    @Override    
    protected void onResume() {
        super.onResume();
    }
    
    /*
     * Called when the Activity is no longer visible.
     */
    @Override
    protected void onStop() {
    	// Disconnecting the client invalidates it.
        mLocationClient.disconnect();
        super.onStop();
    }

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {

		// Inflate the menu; this adds items to the action bar if it is present.
		getMenuInflater().inflate(R.menu.main, menu);
		return true;
	}

	@Override
	public boolean onOptionsItemSelected(MenuItem item) {
		// Handle action bar item clicks here. The action bar will
		// automatically handle clicks on the Home/Up button, so long
		// as you specify a parent activity in AndroidManifest.xml.
		int id = item.getItemId();
		if (id == R.id.action_settings) {
			return true;
		}
		return super.onOptionsItemSelected(item);
	}
	
	// Called when the User clicks the Send Location Button
	
	// sends current Location to the server
	// called when the User clicks the Send Location Now button
	public void sendLocation(View view){
		if(servicesConnected()){		
			Location mLocation = mLocationClient.getLastLocation();
			new ClientTask().execute(serverName, port, packLocation(mLocation));
		} else {
			dispMsg = "Google Play Services not available!\n" + dispMsg;
			((TextView) findViewById(R.id.text_1)).setText(dispMsg);
		}
	}
	
	
	//called when the User clicks the Begin Auto Send button
	public void beginService(View view){
    	if(!AutoSendService.serviceRunning){
			//get interval value in minutes
	    	EditText editText = (EditText) findViewById(R.id.edit_1);
		    long inter = Long.valueOf(editText.getText().toString());
		    //convert to milliseconds
		    long interval = inter * 60 * MILLISECONDS_PER_SECOND; 
	    	
		    // start service
	    	Intent serviceIntent = new Intent(this, AutoSendService.class); 
		    serviceIntent.putExtra("interval", interval);
	    	startService(serviceIntent);
	    	dispMsg ="Auto Sending Location every " + inter + " minutes...\n" + dispMsg;
    	}else{
    		dispMsg = "Auto Send Service already running.\n Use \"End Auto Send\" to stop it.\n" + dispMsg;
    	}
    	((TextView)findViewById(R.id.text_1)).setText(dispMsg);
	}

	//called when the User clicks the End Auto Send button
	public void endService(View view){
		if(AutoSendService.serviceRunning){
			//end service
	    	stopService(new Intent(this, AutoSendService.class));
	    	dispMsg = "Auto Send Service stopped.\n" + dispMsg;
		}else{
			dispMsg = "Auto Send Service is not running.\n Use \"Begin Auto Send\" to start it.\n" + dispMsg;
		}
		((TextView)findViewById(R.id.text_1)).setText(dispMsg);
	}
	   
    private boolean servicesConnected() {
        // Check that Google Play services is available
    	int errorCode = GooglePlayServicesUtil.isGooglePlayServicesAvailable(this);
    	if (errorCode != ConnectionResult.SUCCESS) {
    	  GooglePlayServicesUtil.getErrorDialog(errorCode, this, 0).show();
    	  return false;
    	}
    	return true;
    }
    
    /*
     * Called by Location Services when the request to connect the
     * client finishes successfully. At this point, you can
     * request the current location or start periodic updates
     */
    @Override
    public void onConnected(Bundle dataBundle) {
        // Display the connection status
    	Toast.makeText(this, "Connected", Toast.LENGTH_SHORT).show();
    }
    
    /*
     * Called by Location Services if the connection to the
     * location client drops because of an error.
     */
    @Override
    public void onDisconnected() {
        // Display the connection status
        Toast.makeText(this, "Disconnected. Please re-connect.", Toast.LENGTH_SHORT).show();
    }
    
    
    /*
     * Called by Location Services if the attempt to
     * Location Services fails.
     */
    @SuppressWarnings("deprecation")
	@Override
    public void onConnectionFailed(ConnectionResult connectionResult) {
        /*
         * Google Play services can resolve some errors it detects.
         * If the error has a resolution, try sending an Intent to
         * start a Google Play services activity that can resolve
         * error.
         */
        if (connectionResult.hasResolution()) {
            try {
                // Start an Activity that tries to resolve the error
                connectionResult.startResolutionForResult(
                        this,
                        CONNECTION_FAILURE_RESOLUTION_REQUEST);
                /*
                 * Thrown if Google Play services canceled the original
                 * PendingIntent
                 */
            } catch (IntentSender.SendIntentException e) {
                // Log the error
                e.printStackTrace();
            }
        } else {
            /*
             * If no resolution is available, display a dialog to the
             * user with the error.
             */
            showDialog(connectionResult.getErrorCode());
        }
    }
    
    
    private String packLocation(Location loc){
    	//get the unique device ID
		String devId = Secure.getString(getBaseContext().getContentResolver(), Secure.ANDROID_ID); 
		//Last best location
		
		//get time of location capture
		String datetime = Epoch2DateString(loc.getTime(), "yyyy-MM-dd HH:mm:ss");
		//get location coordinates
		double lat = loc.getLatitude();
		double lon = loc.getLongitude();
		
		//assemble the message
		return preLen(devId)+preLen(datetime)+preLen(String.valueOf(lat))+preLen(String.valueOf(lon));
    }
	
	private String preLen(String str){
		//Prepends the length of the string to the string
		int len = str.length();
		String length = String.valueOf(len);
		//if empty string is passed in, return empty string
		if(len == 0){
			return "";
		}		
		//if length is less than 10, pad with leading zero
		else if(len < 10){
			length = "0" + length;
		}
		//default case
		if(len <= 99){
			return length+str;
		}else{ //string it too big, separate it into chunks
			return "99"+str.substring(0, 98)+"~"+preLen(str.substring(98));			
		}
	}
	
	@SuppressLint("SimpleDateFormat")
	private String Epoch2DateString(long epochSeconds, String formatString) {
	    Date updatedate = new Date(epochSeconds);
	    SimpleDateFormat format = new SimpleDateFormat(formatString);
	    return format.format(updatedate);
	}
	
    /* ClientTask extends AsyncTask to handle sending a location message
     * message is sent to the server specified by (sName, sPort)
     * */    
    public class ClientTask extends AsyncTask<String, Void, String>{
    	
    	protected String doInBackground(String... strings){
    		String sName = strings[0];
    		int sPort = Integer.valueOf(strings[1]);
    		String message = strings[2];
    		Socket socket;
    		try{    			
    			//get the current time
    			Time now = new Time();
    			now.setToNow();   			
    			//get server IP and connect to it
    			InetAddress serverAddr = InetAddress.getByName(sName);    			
    			socket = new Socket(serverAddr, sPort);
    			//send the message
    			PrintWriter out = new PrintWriter(new BufferedWriter(new OutputStreamWriter(socket.getOutputStream())), true);
    			out.println(message);
    			socket.close();
    			//set the text in the Text View
    			return "Location sent @ " + now.format("%H:%M:%S");
    			
    		} catch(UnknownHostException e1){
    			e1.printStackTrace();
    			return e1.getMessage();
    		} catch (IOException e1){
    			e1.printStackTrace();
    			return e1.getMessage();
    		} catch(Exception e){
    			e.printStackTrace();
    			return e.getMessage();
    		}
    	}
    	protected void onProgressUpdate(){}

    	protected void onPostExecute(String msg){
    		dispMsg = msg + "\n" + dispMsg;
    		((TextView) findViewById(R.id.text_1)).setText(dispMsg);
    	}
    }
    
    public static class ErrorDialogFragment extends DialogFragment {
        // Global field to contain the error dialog
        private Dialog mDialog;
        // Default constructor. Sets the dialog field to null
        public ErrorDialogFragment() {
            super();
            mDialog = null;
        }
        // Set the dialog to display
        public void setDialog(Dialog dialog) {
            mDialog = dialog;
        }
        // Return a Dialog to the DialogFragment.
        @Override
        public Dialog onCreateDialog(Bundle savedInstanceState) {
            return mDialog;
        }
    }
    
	/**
	 * A placeholder fragment containing a simple view.
	 */
	public static class PlaceholderFragment extends Fragment {

		public PlaceholderFragment() {
		}

		@Override
		public View onCreateView(LayoutInflater inflater, ViewGroup container,
				Bundle savedInstanceState) {
			View rootView = inflater.inflate(R.layout.fragment_main, container,
					false);
			return rootView;
		}
	}

}
