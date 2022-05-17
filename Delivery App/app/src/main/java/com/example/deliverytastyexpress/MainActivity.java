package com.example.deliverytastyexpress;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import com.loopj.android.http.*;

import cz.msebera.android.httpclient.Header;

public class MainActivity extends AppCompatActivity {
    TextView textview;
    Button btn1,btn2;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        textview = findViewById(R.id.textview);
        btn1 = findViewById(R.id.button);
        btn1.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                String url = "http://192.168.1.163:5000/dasher";
                new AsyncHttpClient().get(url, new AsyncHttpResponseHandler() {
                    @Override
                    public void onSuccess(int statusCode, Header[] headers, byte[] responseBody) {
                        String str = new String(responseBody);
                        textview.setText(str);
                    }

                    @Override
                    public void onFailure(int statusCode, Header[] headers, byte[] responseBody, Throwable error) {
                        textview.setText("No Orders In The Queue, Check Again Later");
                    }
                });

            }
        });
       btn2 = findViewById(R.id.button2);
       btn2.setOnClickListener(new View.OnClickListener() {
           @Override
           public void onClick(View view) {
               String url = "http://192.168.1.163:5000/dasher";
               new AsyncHttpClient().post(url, new AsyncHttpResponseHandler() {
                   @Override
                   public void onSuccess(int statusCode, Header[] headers, byte[] responseBody) {
                       textview.setText("New Order!");
                   }

                   @Override
                   public void onFailure(int statusCode, Header[] headers, byte[] responseBody, Throwable error) {
                        textview.setText("NetWork Error for Post Request");
                   }
               });
           }
       });
    }
}