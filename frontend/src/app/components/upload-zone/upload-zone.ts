import { Component, inject } from '@angular/core';
import { ToastModule } from 'primeng/toast';
import { FileUploadModule } from 'primeng/fileupload';
import { ButtonModule } from 'primeng/button';
import { BadgeModule } from 'primeng/badge';
import { ProgressBarModule } from 'primeng/progressbar';
import { MessageService } from 'primeng/api';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-upload-zone',
  imports: [
    ToastModule,
    FileUploadModule,
    ButtonModule,
    BadgeModule,
    ProgressBarModule,
    CommonModule,
  ],
  templateUrl: './upload-zone.html',
  styleUrl: './upload-zone.css',
  providers: [
    MessageService,
  ],
})
export class UploadZone {

  //
  //   Code imported from the PrimeNG documentation and adapted to the project but mostly raw
  //
  
  private messageService = inject(MessageService);
    files: any[] = [];
    totalSize: number = 0;
    totalSizePercent: number = 0;

    choose(event: Event, callback: () => void) {
        callback();
    }

    onRemoveTemplatingFile(event: any, file: any, removeFileCallback: any, index: any) {
        removeFileCallback(event, index);
        this.totalSize -= parseInt(this.formatSize(file.size));
        this.totalSizePercent = this.totalSize / 10;
    }

    onClearTemplatingUpload(clear: any) {
        clear();
        this.totalSize = 0;
        this.totalSizePercent = 0;
    }

    onTemplatedUpload() {
        this.messageService.add({ severity: 'success', summary: 'Success', detail: 'File Uploaded', life: 3000 });
    }

    onSelectedFiles(event: any) {
        this.files = event.currentFiles;
        this.files.forEach((file) => {
            this.totalSize += parseInt(this.formatSize(file.size));
        });
        this.totalSizePercent = this.totalSize / 10;
    }

    uploadEvent(callback: any) {
        callback();
    }

    formatSize(bytes: any) {
        const k = 1024;
        const dm = 3;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        if (bytes === 0) {
            return `0 ${sizes[0]}`;
        }
        
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        const formattedSize = parseFloat((bytes / Math.pow(k, i)).toFixed(dm));
        
        return `${formattedSize} ${sizes[i]}`;
    }
}
