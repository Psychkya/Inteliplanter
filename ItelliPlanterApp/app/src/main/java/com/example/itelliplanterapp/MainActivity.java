package com.example.itelliplanterapp;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.AsyncTask;
import android.os.Bundle;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Spinner;
import android.widget.Toast;

import com.amazonaws.mobileconnectors.dynamodbv2.document.datatype.Document;

import java.lang.reflect.Array;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class MainActivity extends AppCompatActivity implements AdapterView.OnItemSelectedListener {
    public ArrayList<String> planterName = new ArrayList<String>();
    public ArrayList<String> planterId = new ArrayList<String>();
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        //Toast.makeText(this, "welcome", Toast.LENGTH_LONG).show();

        planterName.add("Choose planter");
        planterId.add("blank");

        GetAllItemsAsyncTask task = new GetAllItemsAsyncTask();
        task.execute();

        Spinner spinner = findViewById(R.id.planterSpinner);
        // Spinner click listener
        spinner.setOnItemSelectedListener(this);
        // Create an ArrayAdapter using the string array and a default spinner layout
        ArrayAdapter<String> adapter = new ArrayAdapter<String>(this,
                android.R.layout.simple_spinner_item,  planterName);
         // Specify the layout to use when the list of choices appears
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
         // Apply the adapter to the spinner
        spinner.setAdapter(adapter);
        adapter.notifyDataSetChanged();
    }

    /** Called when the user taps the Add New button */
    public void newPlanter(View view) {
        Intent intent = new Intent(this, CreateNewPlanter.class);
        startActivity(intent);
    }

    @Override
    public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
        // On selecting a spinner item
        String item = parent.getItemAtPosition(position).toString();
        //Toast.makeText(this, item, Toast.LENGTH_LONG).show();

        if (!item.equals("Choose planter")) {
            Intent intent = new Intent(this, PlanterDashboard.class);
            intent.putExtra("planterID", planterId.get(position));

            startActivity(intent);
        }
    }
    @Override
    public void onNothingSelected(AdapterView<?> arg0) {
        // TODO Auto-generated method stub
    }

    /*public void viewDashboard(View view) {
        Spinner spinner = (Spinner) findViewById(R.id.planterSpinner);
        String text = spinner.getSelectedItem().toString();
        if (text.equals("Living Room Planter")) {
            Intent intent = new Intent(this, PlanterDashboard.class);
            intent.putExtra("plant", "Plant Type: Rose");
            intent.putExtra("age", "Growing Since: 05/12/2020");
            intent.putExtra("error", "ATTENTION: Please refill the water tank");
            intent.putExtra("moisture", "Moisture Level: Medium Moisture");
            intent.putExtra("light", "Light Exposure: 1 hr left");
            startActivity(intent);
        }else if(text.equals("Office Planter")){
            Intent intent=new Intent(this, PlanterDashboard.class);
            intent.putExtra("plant", "Plant Type: Cactus");
            intent.putExtra("age", "Growing Since: 01/30/2019");
            intent.putExtra("error", "Conditions are optimal =)");
            intent.putExtra("moisture", "Moisture Level: Low Moisture");
            intent.putExtra("light", "Light Exposure: 5 hr left");
            startActivity(intent);
        }else if(text.equals("Select Planter")){

        }
    }*/

    /**
     * Async Task for handling the network retrieval of all the memos in DynamoDB
     */
   private class GetAllItemsAsyncTask extends AsyncTask<Void, Void, ArrayList<String>> {
        @Override
        protected ArrayList<String> doInBackground(Void... params) {
            DatabaseAccess databaseAccess = DatabaseAccess.getInstance(MainActivity.this);
            List<Document> results = databaseAccess.getAllPlanters();
            for (Document planter:results) {
                planterName.add(planter.get("planterName").asString());
                planterId.add(planter.get("PlanterId").asString());
            }
            return planterName;
        }
    }
}