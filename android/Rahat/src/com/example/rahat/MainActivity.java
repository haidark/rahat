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

import android.app.Dialog;
import android.app.DialogFragment;
import android.content.IntentSender;
import android.location.Location;
import android.os.Bundle;
import android.provider.Settings.Secure;
import android.support.v4.app.Fragment;
import android.support.v7.app.ActionBarActivity;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import com.google.android.gms.common.ConnectionResult;
import com.google.android.gms.common.GooglePlayServicesClient;
import com.google.android.gms.common.GooglePlayServicesUtil;
import com.google.android.gms.location.LocationClient;

public class MainActivity extends ActionBarActivity implements
GooglePlayServicesClient.ConnectionCallbacks,
GooglePlayServicesClient.OnConnectionFailedListener  {
	// Global constants
    /*
     * Define a request code to send to Google Play services
     * This code is returned in Activity.onActivityResult
     */
    private final static int CONNECTION_FAILURE_RESOLUTION_REQUEST = 9000;
	private LocationClient mLocationClient;
	private Location mCurrentLocation;
    private static final String SERVERIP ="192.168.1.222";
    private static final int SERVERPORT = 1060;
    private Socket socket;
	
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_main);
		/*
         * Create a new location client, using the enclosing class to
         * handle callbacks.
         */
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
        // Connect the client.
        mLocationClient.connect();
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
	public void sendLocation(View view){
		//do something in response to button press
		
		//get string from editText field
		EditText editText = (EditText) findViewById(R.id.edit_1);
		String phrase = editText.getText().toString();
		
		//get the unique device ID
		String devId = Secure.getString(getBaseContext().getContentResolver(),
                Secure.ANDROID_ID); 
		
		//get the time & location
		mCurrentLocation = mLocationClient.getLastLocation();
		long time = mCurrentLocation.getTime();
		String datetime = Epoch2DateString(time/1000, "yyyy-MM-dd HH:mm:ss");
		double lat = mCurrentLocation.getLatitude();
		double lon = mCurrentLocation.getLongitude();
		
		//set the text in the Text View
		String dispMsg = preLen(phrase)+"\n"+preLen(devId)+"\n"+preLen(datetime)+"\n"+preLen(String.valueOf(lat))+"\n"+preLen(String.valueOf(lon));
		((TextView) findViewById(R.id.text_1)).setText(dispMsg); 
		
		//send the message to the server
		String sendMsg = preLen(phrase)+preLen(devId)+preLen(datetime)+preLen(String.valueOf(lat))+preLen(String.valueOf(lon));
		//open a socket
		new Thread(new ClientThread()).start();
		try{
			PrintWriter out = new PrintWriter(new BufferedWriter(new OutputStreamWriter(socket.getOutputStream())), true);
			out.println(sendMsg);
		}catch(UnknownHostException e) {
			e.printStackTrace();
		}catch(IOException e){
			e.printStackTrace();
		}catch(Exception e){
			e.printStackTrace();
		}

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
	
	public static String Epoch2DateString(long epochSeconds, String formatString) {
	    Date updatedate = new Date(epochSeconds * 1000);
	    SimpleDateFormat format = new SimpleDateFormat(formatString);
	    return format.format(updatedate);
	}
	
	// Define a DialogFragment that displays the error dialog
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
        Toast.makeText(this, "Disconnected. Please re-connect.",
                Toast.LENGTH_SHORT).show();
    }
    
    /*
     * Called by Location Services if the attempt to
     * Location Services fails.
     */
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
    
    class ClientThread implements Runnable{
    	@Override
    	public void run(){
    		try{
    			InetAddress serverAddr = InetAddress.getByName(SERVERIP);    			
    			socket = new Socket(serverAddr, SERVERPORT);
    		} catch(UnknownHostException e1){
    			e1.printStackTrace();
    		} catch (IOException e1){
    			e1.printStackTrace();
    		}catch(Exception e){
    			e.printStackTrace();
    		}
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