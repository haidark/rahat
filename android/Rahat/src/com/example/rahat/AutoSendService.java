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

import com.google.android.gms.common.ConnectionResult;
import com.google.android.gms.common.GooglePlayServicesClient;
import com.google.android.gms.common.GooglePlayServicesUtil;
import com.google.android.gms.location.LocationClient;
import com.google.android.gms.location.LocationListener;
import com.google.android.gms.location.LocationRequest;

import android.annotation.SuppressLint;
import android.app.Notification;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Intent;
import android.location.Location;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.IBinder;
import android.provider.Settings.Secure;
import android.text.format.Time;
import android.util.Log;
import android.widget.Toast;

public class AutoSendService extends Service implements 
		GooglePlayServicesClient.ConnectionCallbacks,
		GooglePlayServicesClient.OnConnectionFailedListener,
		LocationListener {
	private LocationClient mLocationClient;
	private LocationRequest mLocationRequest;
	private long interval;
	public static boolean serviceRunning = false;
	private static int ONGOING_NOTIFICATION_ID = 110491;

	@Override
	public void onCreate() {		
		super.onCreate();
		//start a location client if google play services are available
		int resp = GooglePlayServicesUtil.isGooglePlayServicesAvailable(this);
	    if (resp == ConnectionResult.SUCCESS) {
	        mLocationClient = new LocationClient(this, this, this);
	        mLocationClient.connect();
	        
	    } else {
	        Toast.makeText(this, "Google Play Service Error " + resp,
	                Toast.LENGTH_LONG).show();
	    }

	    //let the outside world know service is running
	    serviceRunning = true;
		Log.d("AutoSendService", "Create");
	}
	
	@SuppressWarnings("deprecation")
	@Override
	public int onStartCommand(Intent intent, int flags, int startId) {
	    //get the users interval value
		Bundle extras = intent.getExtras();
	    interval = (long) extras.get("interval");
	    String notifMsg = "Sending Location every " + interval/60/1000 + " minutes";
	    
	    //make the service a foreground service with this notification
	    Notification notification = new Notification(R.drawable.ic_launcher, getText(R.string.notif_text), System.currentTimeMillis());
	    Intent notificationIntent = new Intent(this, MainActivity.class);
	    PendingIntent pendingIntent = PendingIntent.getActivity(this, 0, notificationIntent, 0);
	    notification.setLatestEventInfo(this, getText(R.string.notification_title), notifMsg, pendingIntent);
	    startForeground(ONGOING_NOTIFICATION_ID, notification);
		
	    Log.d("AutoSendService", "Interval value is: " + interval);	    
		return START_STICKY;
	}
	
	@Override
	public IBinder onBind(Intent arg0) {
		// No binding
		return null;
	}
	
	@Override
	public void onDestroy() {
		mLocationClient.removeLocationUpdates(this);
		mLocationClient.disconnect();
		Log.d("AutoSendService", "Destroy");
		serviceRunning = false;
		super.onDestroy();		
	}
	
	@Override
	public void onLocationChanged(Location location) {		
		String msg = packLocation(location);
		new ClientTask().execute(MainActivity.serverName, MainActivity.port, packLocation(location));
		
		//get the current time
		Time now = new Time();
		now.setToNow();
		//Toast to show location was sent
		Toast.makeText(this, "Location sent at " + now.format("%H:%M:%S"), Toast.LENGTH_LONG).show();
		Log.d("AutoSendService", msg);
	}
	
	@Override
	public void onConnected(Bundle connectionHint) {
		if (mLocationClient != null && mLocationClient.isConnected()) {
   	
	        mLocationRequest = LocationRequest.create();
	        mLocationRequest.setInterval(interval)
	        		.setFastestInterval(interval)
	                .setPriority(LocationRequest.PRIORITY_HIGH_ACCURACY)
	                .setSmallestDisplacement(0);

	        mLocationClient.requestLocationUpdates(mLocationRequest, this);	        
	    }
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
    @Override
    public void onConnectionFailed(ConnectionResult connectionResult) {
    	Toast.makeText(this, "Connection Failed!", Toast.LENGTH_SHORT).show();
    }
    
    private String packLocation(Location loc){
    	//get the unique device ID
		String devId = Secure.getString(getContentResolver(), Secure.ANDROID_ID); 
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
	
	/* ClientThread extends AsyncTask to handle sending a location message
     * message is sent to the server specified by (sName, sPort)
     * */    
    public class ClientTask extends AsyncTask<String, Void, String>{
    	
    	protected String doInBackground(String... strings){
    		String sName = strings[0];
    		int sPort = Integer.valueOf(strings[1]);
    		String message = strings[2];
    		Socket socket;
    		try{    			
    			
    						
    			//get server IP and connect to it
    			InetAddress serverAddr = InetAddress.getByName(sName);    			
    			socket = new Socket(serverAddr, sPort);
    			//send the message
    			PrintWriter out = new PrintWriter(new BufferedWriter(new OutputStreamWriter(socket.getOutputStream())), true);
    			out.println(message);
    			socket.close();
    			//set the text in the Text View
    			return "";
    			
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
    		
    	}
    }
}
