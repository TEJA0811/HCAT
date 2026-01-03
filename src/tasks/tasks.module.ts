import { Module } from '@nestjs/common';
import { TasksService } from './tasks.service';
import { TasksController } from './tasks.controller';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Project } from '../projects/entities/project.entity';
import { Manager } from '../managers/entities/manager.entity';
import { User } from '../users/entities/user.entity';
import { Task } from './entities/task.entity';

@Module({
  imports: [TypeOrmModule.forFeature([Project,Manager,User,Task
  ])],
  controllers: [TasksController],
  providers: [TasksService],
})
export class TasksModule {}
