import { Component } from '@angular/core';
import { Map } from '../../map/map';
import { UploadZone } from '../../upload-zone/upload-zone';

@Component({
  selector: 'app-home',
  imports: [Map, UploadZone],
  templateUrl: './home.html',
  styleUrl: './home.css',
})
export class Home {
  
}
