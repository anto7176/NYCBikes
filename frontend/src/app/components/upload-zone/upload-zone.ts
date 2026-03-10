import { Component, computed, inject, input, signal } from '@angular/core';
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
  //   Interfaces
  //
  
  private readonly messageService = inject(MessageService);

  // INPUTS

  public readonly importType = input.required<string>();

  //
  //   Constants
  //
  
  protected readonly MAX_FILE_SIZE = 1073741824;

  //
  //   Data
  //
  
  protected readonly files = signal<any[]>([]);
  protected readonly totalSize = signal<number>(0);

  //
  //   States
  //
  
  protected readonly isUploading = signal<boolean>(false);

  //
  //   Computed
  //
  
  protected readonly totalSizePercent = computed(() => {
    return this.totalSize() / this.MAX_FILE_SIZE * 100;
  });

  //
  //   Methods
  //

  public onRemoveTemplatingFile(event: any, file: any, removeFileCallback: any, index: any) {
    removeFileCallback(event, index);

    this.totalSize.update(
      (totalSize) => 
        totalSize - Number.parseInt(file.size)
    );
  }

  public onTemplatedUpload() {
    this.messageService.add(
      { severity: 'success', summary: 'Success', detail: 'File Uploaded', life: 3000 }
    );

    this.totalSize.set(0);
    this.isUploading.set(false);
  }

  public onSelectedFiles(event: any) {
    this.files.set(event.currentFiles);

    this.files().forEach((file) => {
        this.totalSize.update(
          (totalSize) => totalSize + Number.parseInt(file.size)
        );
    });
  }

  public onError(event: any) {
    this.isUploading.set(false);
    this.messageService.add(
      { severity: 'error', summary: 'Unexpected error', detail: event.error.error.detail, life: 3000 }
    );
  }

  public upload(callback: any) {
    this.isUploading.set(true);
    callback();
  }

  public formatSize(bytes: any) {
    const k = 1024;
    const dm = 3;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];

    if (bytes === 0) {
        return `0 ${sizes[0]}`;
    }
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    const formattedSize = Number.parseFloat(
      (bytes / Math.pow(k, i)).toFixed(dm)
    );
    
    return `${formattedSize} ${sizes[i]}`;
  }
}
